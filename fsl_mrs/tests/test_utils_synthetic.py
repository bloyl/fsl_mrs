from fsl_mrs.utils import synthetic as syn
from fsl_mrs.utils.misc import FIDToSpec
from fsl_mrs.core import MRS
import numpy as np
from pathlib import Path

testsPath = Path(__file__).parent
basis_path = testsPath / 'testdata/fsl_mrs/steam_basis'


def test_noisecov():
    # Create positive semi-definite noise covariance
    inputnoisecov = np.random.random((2,2))
    inputnoisecov= np.dot(inputnoisecov,inputnoisecov.T) 

    testFID,hdr = syn.syntheticFID(coilamps=[1.0,1.0],
                    coilphase=[0.0,0.0],
                    noisecovariance=inputnoisecov,
                    amplitude=[0.0,0.0],
                    points= 32768)

    outcov = np.cov(np.asarray(testFID))

    # Noise cov is for both real and imag, so multiply by 2
    assert np.isclose(outcov,2*inputnoisecov,atol=1E-1).all()

def test_syntheticFID():
    testFID,hdr = syn.syntheticFID(noisecovariance=[[0.0]],points=16384)

    # Check FID is sum of lorentzian lineshapes
    # anlytical solution
    T2 = 1/(hdr['inputopts']['damping'][0])
    M0 = hdr['inputopts']['amplitude'][0]
    f0 = hdr['inputopts']['centralfrequency']*hdr['inputopts']['chemicalshift'][0]
    f1 = hdr['inputopts']['centralfrequency']*hdr['inputopts']['chemicalshift'][1]
    f = hdr['faxis']
    spec = (M0*T2)/(1+4*np.pi**2*(f0-f)**2*T2**2) +1j*(2*np.pi*M0*(f0-f)*T2**2)/(1+4*np.pi**2*(f0-f)**2*T2**2)
    spec += (M0*T2)/(1+4*np.pi**2*(f1-f)**2*T2**2) +1j*(2*np.pi*M0*(f1-f)*T2**2)/(1+4*np.pi**2*(f1-f)**2*T2**2)

    # Can't quite get the scaling right here.
    testSpec = FIDToSpec(testFID[0])
    spec /= np.max(np.abs(spec))
    testSpec /= np.max(np.abs(testSpec))

    assert np.isclose(spec,FIDToSpec(testFID[0]),atol = 1E-2,rtol = 1E0).all()


def test_syntheticFromBasis():
    # TO DO
    pass


def test_syntheticFromBasis_baseline():

    fid, header, _ = syn.syntheticFromBasisFile(str(basis_path),
                                                baseline=((0.0, 0.0),),
                                                concentrations={'Mac': 2.0},
                                                noisecovariance=[[0.0]])

    mrs = MRS(FID=fid, header=header)
    mrs.conj_FID()

    fid, header, _ = syn.syntheticFromBasisFile(str(basis_path),
                                                baseline=((1.0, 1.0),),
                                                concentrations={'Mac': 2.0},
                                                noisecovariance=[[0.0]])

    mrs2 = MRS(FID=fid, header=header)
    mrs2.conj_FID()

    assert np.allclose(mrs2.get_spec(), mrs.get_spec() + np.complex(1.0, -1.0))
