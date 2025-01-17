This document contains the FSL-MRS release history in reverse chronological order.

1.1.5 (Wednesday 11th August 2021)
----------------------------------
- Updated example MRSI data to conform to NIfTI-MRS standard.
- Quantification will not fail if volume fractions do not sum exactly to 1.0 (to within 1E-3).
- fixed bug in fsl_mrsi looking for TE in wrong header structure.
- New mrs_tools command 'conjugate' to help fix NIfTI-MRS data with the wrong phase/frequency convention.
- basis_tools remove has number of HLSVD components reduced to stop odd broad resonance behaviour.
- fsl_mrs_proc align can now align across all higher dimension FIDs. Pass 'all' as dimension tag.
- New command "fsl_mrs_proc model". HSLVD modelling of peaks in defined region. Number of components settable.
- Updates to basis set simulator. Non-uniform slice select gradients are now handled.

1.1.4 (Tuesday 3rd August 2021)
-------------------------------
- Fixed bug in calculation of molality concentration. Tissue mole fractions had been swapped for tissue volume fractions. Molar concentrations unaffected.
- Fixed bug in mrs_tools split
- Fixed bug in alignment of multi-dimensional data.
- Fixed bug in fsl_mrsi: data without a water reference now works.
- fsl_mrsi now outputs fitting nuisance parameters: phases, and shifts & linewidths for each metabolite group.
- Add NIfTI-MRS reshape command
- Add basis_tools remove_peak option to run HLSVD, typical usage for removing TMS peak.
- Added an add_water_peak method to MRS class.
- Updated fit_FSLModel defaults to match fsl_mrs command line defaults.

1.1.3 (Tuesday 29th June 2021)
------------------------------
- Added mrs_tools script. Replaces mrs_vis and mrs_info. Adds split/merge/reorder functionality.
- Added basis_tools script. Tools for manipulating (shifting, scaling, converting, differencing, conjugating, and adding to) basis sets.
- Improved display of basis sets using mrs_tools or basis_tools.
- Added 'default' MEGA-PRESS MM option to fsl_mrs and mrs class.
- Preprocessing tools now add processing provenance information to NIfTI-MRS files.
- Under the hood refactor of basis, MRS, and MRSI classes.
- Updated density matrix simulator. Added some automatic testing.
- Added documentation about the results_to_spectrum script.

1.1.2 (Friday 16th April 2021)
------------------------------
- Added 2H information
- Bug fixes
- Added documentation around installation from conda

1.1.1 (Monday 15th March 2021)
------------------------------
- SNR measurements should cope with negative peak amplitudes correctly
- New metabolites added to list of default water referencing metabolites (Cr, PCr and NAA)
- Quantification now takes into account T1 relaxation
- Quantification module now fits the water reference FID to deal with corruption of first FID points.
- Added plot in report to clarify referencing signals.
- Restructure of internal quantification code.

1.1.0 (Thursday 18th February 2021)
-----------------------------------
- Support for NIfTI-MRS format.
- Preprocessing scripts reoriented around NIfTI-MRS framework
- New script results_to_spectrum for generating full fits in NIfTI-MRS format from fsl_mrs results.
- Documentation and example data updated for move to NIfTI-MRS.
- Added mrs_info command to give quick text summary of NIfTI-MRS file contents.
- Updates to the WIP dynamic fitting module.

1.0.6 (Tuesday 12th January 2021)
---------------------------------
- Internal changes to core MRS class.
- New plotting functions added, utility functions for plotting added to MRS class.
- fsl_mrs/aux folder renamed for Windows compatibility.
- Moved online documentation to open.win.ox.ac.uk/pages/fsl/fsl_mrs/.
- Fixed small bugs in preprocessing display.
- Synthetic spectra now use fitting model directly.
- Bug fixes in the fsl_Mrs commandline interface. Thanks to Alex Craig-Craven.
- WIP: Dynamic fitting model and dynamic experiment simulation.
- spec2nii requirement pinned to 0.2.11 during NIfTI-MRS development.

1.0.5 (Friday 9th October 2020)
-------------------------------
- Extended documentation of hardcoded constants, including MCMC priors.
- Extended documentation of synthetic macromolecules.
- Added flag to MCMC optimise baseline parameters.

1.0.4 (Friday 14th August 2020)
-------------------------------
- Fixed bug in automatic conjugation facility of fsl_mrs_preproc
- jmrui text file reader now handles files with both FID and spectra

1.0.3 (Friday 10th July 2020)
-----------------------------
- Changed to pure python version of HLSVDPRO (hlsvdpropy). Slight speed penalty
  but hopefully reduced cross-compilation issues.
- fsl_mrs_preproc now outputs zipped NIFTI files to match the rest of the command-line   scripts.
- Apodisation option added to alignment in fsl_mrs_proc and fsl_mrs_preproc. Reduces effect of noise. Default value is 10 Hz of exponential apodisation.
- Fixed phasing subcommand added to fsl_mrs_proc allowing the user to apply a fixed 0th and 1st order phase.
- mrs_vis now handles folders as an input for MRS data (still handles folders of basis files).
- Conjugation command added to fsl_mrs_proc.
- fsl_mrs_preproc automatically conjugates input spectra if required.
- Typos and small bug fixes.
- Documentation expanded.

1.0.2 (Saturday 27th June 2020)
--------------------------------
- Add missing requirement (pillow)

1.0.1 (Friday 19th June 2020)
--------------------------------
- Output folder in fsl_mrs_proc will now be created if it does not exist.
- fsl_mrs_proc now handles data with a singleton coil dimension correctly.
- --ind_scale and --disable_MH_priors options added to fsl_mrs and fsl_mrsi.

1.0.0 (Wednesday 17th June 2020)
--------------------------------
- First public release of package.
