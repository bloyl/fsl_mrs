# lcm_io.py - I/O utilities for LCModel file formats in FSL_MRS
#
# Author: Saad Jbabdi <saad@fmrib.ox.ac.uk>
#         Will Clarke <william.clarke@ndcn.ox.ac.uk>
#
# Copyright (C) 2020 University of Oxford
# SHBASECOPYRIGHT

import scipy.signal as ss
import numpy as np
import os
import re
from fsl_mrs.utils.misc import checkCFUnits
from fsl_mrs.core.nifti_mrs import gen_new_nifti_mrs


# Raw file reading
def readLCModelRaw(filename, unpack_header=True, conjugate=True):
    """
    Read LCM format file

    :param filename: Path to .RAW/.H2O file
    :param bool conjugate: Apply conjugation upon read

    :return: data
    :return: header
    """
    header = []
    data   = []
    in_header = False
    with open(filename, 'r') as f:
        for line in f:
            if (line.find('$') > 0):
                in_header = True
            if in_header:
                header.append(line)
            else:
                data.append(list(map(float, line.split())))

            if line.find('$END') > 0:
                in_header = False

    # Reshape data
    data = np.concatenate([np.array(i) for i in data])
    data = (data[0::2] + 1j * data[1::2]).astype(complex)

    # LCModel-specific conjugation
    if conjugate:
        data = np.conj(data)

    # Tidy header info
    if unpack_header:
        header = unpackHeader(header)

    return data, header


def read_lcm_raw_h2o(filename):
    """
    Read LCM format .RAW or .H2O file

    :param filename: Path to .RAW/.H2O file

    :return: NIFTI_MRS
    """
    data, header = readLCModelRaw(filename)
    data = data.reshape((1, 1, 1) + data.shape)

    return gen_new_nifti_mrs(data, header['dwelltime'], header['centralFrequency'])


# Read .RAW basis files
def read_basis_files(basisfiles, ignore=[]):
    """
     Reads basis files and extracts name of metabolite from file name
     Assumes .RAW files are FIDs (not spectra)
     Comes without any header information unfortunately.
    """
    basis = []
    names = []
    for file in basisfiles:
        data, header = readLCModelRaw(file)
        name = os.path.splitext(os.path.split(file)[-1])[-2]
        if name not in ignore:
            names.append(name)
            basis.append(data)
    basis = np.asarray(basis).astype(complex).T
    return basis, names


# Read .BASIS files
def readLCModelBasis(filename, N=None, doifft=True, conjugate=True):
    """
    Read .BASIS format file
    Parameters
    ----------
    filename : string
        Name of .BASIS file

    Returns
    -------
    array-like
        Complex data
    string
        Metabolite names
    string
        Header information

    """
    metabo = []
    # do not conjugate here - this reads a spectrum!
    data, header = readLCModelRaw(filename, unpack_header=False, conjugate=False)

    # extract metabolite names and shifts
    metabo, shifts = siv_basis_header(header)

    if len(metabo) > 1:
        data = data.reshape(len(metabo), -1).T

    # apply ppm shift found in header
    for idx in range(data.shape[1]):
        data[:, idx] = np.roll(data[:, idx], -shifts[idx])

    # Resample if necessary? --> should not be allowed actually
    if N is not None:
        if N != data.shape[0]:
            data = ss.resample(data, N)

    # if freq domain --> turn to time domain
    if doifft:
        data = np.fft.ifft(data, axis=0)

    if conjugate:
        data = np.conj(data)

    # deal with single metabo case
    if len(data.shape) == 1:
        data = data[:, None]
        if len(metabo) == 0:
            metabo = ['Unknown']

    # This will further extract dwelltime, useful if it is not matching
    # the FID
    header = unpackHeader(header)

    # Duplicate header so that it matches all the other basis read functions
    headers = [header] * len(metabo)

    return data, metabo, headers


# Utility functions for above functions
def tidy(x):
    """
      removes ',' from string x
    """
    return x.lower().replace(',', '')


def unpackHeader(header):
    """
       Extracts useful info from header into dict

       Including central frequency, dwelltime, echotime
    """

    tidy_header = dict()
    tidy_header['centralFrequency'] = None
    tidy_header['bandwidth'] = None
    tidy_header['echotime'] = None
    for line in header:
        if line.lower().find('hzpppm') > 0:
            tidy_header['centralFrequency'] = float(tidy(line).split()[-1]) * 1E6
        if line.lower().find('dwelltime') > 0:
            tidy_header['dwelltime'] = float(tidy(line).split()[-1])
            tidy_header['bandwidth'] = 1 / float(tidy(line).split()[-1])
        if line.lower().find('echot') > 0:
            tidy_header['echotime'] = float(tidy(line).split()[-1]) / 1e3  # convert to secs
        if line.lower().find('badelt') > 0:
            tidy_header['dwelltime'] = float(tidy(line).split()[-1])
            tidy_header['bandwidth'] = 1 / float(tidy(line).split()[-1])

    return tidy_header


def siv_basis_header(header):
    """
      extracts metab names and ishift
    """
    metabo = []
    shifts = []
    for txt in header:
        if txt.lower().find('metabo') > 0:
            if txt.lower().find('metabo_') < 0:
                content = re.search(r"'\s*([^']+?)\s*'", txt).groups()[0]
                metabo.append(content)
        if txt.lower().find('ishift') > 0:
            shifts.append(int(tidy(txt).split()[-1]))

    return metabo, shifts


# Write functions
def saveRAW(filename, FID, info=None, hdr=None, conj=False):
    """
      Save .RAW file

      Parameters
      ----------
      filename : string
      FID      : array-like
      info     : dict
             Stores info[key] = value in header
    """
    # Seq par section
    if hdr is not None:
        if 'EchoTime' in hdr:
            TE = hdr['EchoTime']
        else:
            TE = 0.0
        seqpar_header = {'hzpppm': checkCFUnits(hdr['centralFrequency'], units='MHz'),
                         'dwellTime': hdr['dwelltime'],
                         'NumberOfPoints': FID.size,
                         'echot': TE}

    # info (and NMID) section must contain FMTDAT
    if info is None:
        info = {'FMTDAT': '(2E16.6)'}
    elif 'FMTDAT' not in info:
        info.update({'FMTDAT': '(2E16.6)'})

    rFID = np.real(FID)[:, None]
    if conj:
        iFID = -1.0 * np.imag(FID)[:, None]
    else:
        iFID = np.imag(FID)[:, None]

    with open(filename, 'w') as my_file:
        if hdr is not None:
            writeLCMSection(my_file, 'SEQPAR', seqpar_header)
        writeLCMSection(my_file, 'NMID', info)

        for (r, i) in zip(rFID, iFID):
            my_file.write(f'{float(r):16.6E}{float(i):16.6E}\n')


def writeLcmInFile(outfile,
                   meabNames,
                   outDir,
                   seqname,
                   paramDict,
                   shift=0.0,
                   echotime=0.0):
    """
      Save a LCModel .IN file (for basis creation)

      Parameters
      ----------
      outfile   : string
      meabNames : list of stings
      outDir    : string
            Path to location of makebasis call
      seqname   : string
      paramDict : dict
            Stores info[key] = value in header
      shift     : float
            Rx chemical shift to apply to reference
            peak position indicator
      echotime  : float
            Echo time in ms
    """
    seqPar = {'seq': seqname,
              'echot': echotime,
              'fwhmba': paramDict['width'] / paramDict['centralFrequency']}

    nmall = {'hzpppm': paramDict['centralFrequency'],
             'deltat': paramDict['dwelltime'],
             'nunfil': paramDict['points'],
             'filbas': os.path.join(outDir, seqname + '.BASIS'),
             'filps': os.path.join(outDir, seqname + '.PS'),
             'autosc': False,
             'autoph': False,
             'idbasi': seqname}
    nmeachList = []
    for n in meabNames:
        nmeachList.append({'filraw': os.path.join(outDir, n + '.RAW'),
                           'metabo': n,
                           'degzer': 0,
                           'degppm': 0,
                           'conc': 1.0,
                           'ppmapp': [0.1 - shift, -0.4 - shift]})

    # Write file
    with open(outfile, 'w') as my_file:
        # Write seqpar section
        writeLCMSection(my_file, 'seqPar', seqPar)
        # Write nmall section
        writeLCMSection(my_file, 'nmall', nmall)
        # Write nmeach sections
        for n in nmeachList:
            writeLCMSection(my_file, 'nmeach', n)


def writeLCMSection(fobj, sectiontitle, paramdict):
    """
    Write a subsection in an LCModel style file.
    Lines have a white space at the start and the section
    is bracketed with " $sectiontitle" and " $END"

    Parameters
      ----------
        fobj            :   file object
        sectiontitle    :   string
        paramdict       :   dict
                Dictionary where each key value pair
                will be printed on a new line.
    """
    def write(x):
        return fobj.write(' ' + x + '\n')

    write(f'${sectiontitle}')
    for k in paramdict:
        if isinstance(paramdict[k], str):
            write(f'{k}=\'{paramdict[k]}\'')
        elif isinstance(paramdict[k], bool):
            if paramdict[k]:
                write(f'{k}=.true')
            else:
                write(f'{k}=.false')
        elif isinstance(paramdict[k], list):
            tmpString = ','.join(map(str, paramdict[k]))
            write(f'{k}={tmpString}')
        else:
            write(f'{k}={paramdict[k]}')
    write('$END')
