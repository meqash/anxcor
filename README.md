
![](https://github.com/uofuseismo/anxcor/blob/master/git_images/anxcor.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.png)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/uofuseismo/anxcor.png?branch=master)](https://travis-ci.org/uofuseismo/anxcor)
![PyPI](https://img.shields.io/pypi/v/anxcor.png?color=blue&style=plastic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/anxcor.png?style=plastic)
![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/uofuseismo/anxcor/badge.svg?branch=master)](https://coveralls.io/github/uofuseismo/anxcor?branch=master)


## ANXCOR: Ambient Noise X (cross) Correlation

## *Currently in Beta!*

**ANXCOR** is a python library for performing seismic ambient noise crosscorrelations.

ANXCOR's goal is to provide a framework to reproduce academic studies, rapididly prototype experimental workflows,
and produce medium-sized arrays of seismic noise cross-correlations. Anxcor was designed from the outset with readability and explicit documentation in mind, with the overall architecture following most of the practices outlined in the [Clean Code Handbook by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882).


ANXCOR integrates seamlessly into the current python datascience stack by leveraging common datascience packages 
like [pandas](http://pandas.pydata.org), [NumPy](http://www.numpy.org), and [SciPy](http://www.scipy.org), 
as well as the popular seismology package [ObsPy](https://github.com/obspy/obspy/wiki). 
Furthermore, we leverage both [xarray](http://xarray.pydata.org/en/stable/) and [dask](http://dask.org)
to achieve embarassingly parallel execution. Use of these popular packages makes working with ANXCOR intuitive,
concise, and extensible without deep domain experience in compiled languages.

## Documentation

learn more about ANXCOR at the [wiki](https://github.com/uofuseismo/anxcor/wiki).


## Acknowledgements
Kevin A. Mendoza served as chief architect and programmer of ANXCOR. Development of the project was inspired by Dr. Fan-Chi Lin's work in Ambient Noise Seismic Tomography. Many of the routines implemented here were written after careful consultation with him and his Graduate Student work group (However, none of their code was copied or directly translated into anxcor). 

## Attribution
Mendoza, Kevin Anthony, Ben Baker, and Kristine L. Pankow. "ANXCOR: Ambient Noise Cross-Correlation with Python." AGU Fall Meeting 2019. AGU, 2019.

## Known Issues

* Using obsplus Wavebank creates runtime race condition on hdf5 table reading, causing index corruption. Error not encountered if restricting workers to a single thread.

* Returned DataSet requires some unravelling to properly plot. 

* ObsPy is currently not updated to be compatible with numpy 1.17.x or greater. This means that tests directly comparing obspy to anxcor are expected to fail whenever FFT or detrend operations are compared between the two packages. An inspection of these failing tests has confirmed that these errors are numerical in nature, not algorithmic. 
## Planned Enhancements

- FTAN and beamforming routines

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Contributors
- PhD Student Kevin A. Mendoza was the primary developer, and is responsible for the original architecture of the project.

## LICENSE

Copyright 2019 Kevin A Mendoza

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.


