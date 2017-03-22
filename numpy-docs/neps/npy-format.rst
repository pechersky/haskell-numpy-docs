=====================================
A Simple File Format for NumPy Arrays
=====================================

Author: Robert Kern <robert.kern@gmail.com>
Status: Draft
Created: 20-Dec-2007


Abstract
--------

We propose a standard binary file format (NPY) for persisting
a single arbitrary NumPy array on disk.  The format stores all of
the shape and dtype information necessary to reconstruct the array
correctly even on another machine with a different architecture.
The format is designed to be as simple as possible while achieving
its limited goals.  The implementation is intended to be pure
Python and distributed as part of the main numpy package.


Rationale
---------

A lightweight, omnipresent system for saving NumPy arrays to disk
is a frequent need.  Python in general has pickle [1] for saving
most Python objects to disk.  This often works well enough with
NumPy arrays for many purposes, but it has a few drawbacks:

- Dumping or loading a pickle file require the duplication of the
  data in memory.  For large arrays, this can be a showstopper.

- The array data is not directly accessible through
  memory-mapping.  Now that numpy has that capability, it has
  proved very useful for loading large amounts of data (or more to
  the point: avoiding loading large amounts of data when you only
  need a small part).

Both of these problems can be addressed by dumping the raw bytes
to disk using ndarray.tofile() and numpy.fromfile().  However,
these have their own problems:

- The data which is written has no information about the shape or
  dtype of the array.

- It is incapable of handling object arrays.

The NPY file format is an evolutionary advance over these two
approaches.  Its design is mostly limited to solving the problems
with pickles and tofile()/fromfile().  It does not intend to solve
more complicated problems for which more complicated formats like
HDF5 [2] are a better solution.


Use Cases
---------

- Neville Newbie has just started to pick up Python and NumPy.  He
  has not installed many packages, yet, nor learned the standard
  library, but he has been playing with NumPy at the interactive
  prompt to do small tasks.  He gets a result that he wants to
  save.

- Annie Analyst has been using large nested record arrays to
  represent her statistical data.  She wants to convince her
  R-using colleague, David Doubter, that Python and NumPy are
  awesome by sending him her analysis code and data.  She needs
  the data to load at interactive speeds.  Since David does not
  use Python usually, needing to install large packages would turn
  him off.

- Simon Seismologist is developing new seismic processing tools.
  One of his algorithms requires large amounts of intermediate
  data to be written to disk.  The data does not really fit into
  the industry-standard SEG-Y schema, but he already has a nice
  record-array dtype for using it internally.

- Polly Parallel wants to split up a computation on her multicore
  machine as simply as possible.  Parts of the computation can be
  split up among different processes without any communication
  between processes; they just need to fill in the appropriate
  portion of a large array with their results.  Having several
  child processes memory-mapping a common array is a good way to
  achieve this.


Requirements
------------

The format MUST be able to:

- Represent all NumPy arrays including nested record
  arrays and object arrays.

- Represent the data in its native binary form.

- Be contained in a single file.

- Support Fortran-contiguous arrays directly.

- Store all of the necessary information to reconstruct the array
  including shape and dtype on a machine of a different
  architecture.  Both little-endian and big-endian arrays must be
  supported and a file with little-endian numbers will yield
  a little-endian array on any machine reading the file.  The
  types must be described in terms of their actual sizes.  For
  example, if a machine with a 64-bit C "long int" writes out an
  array with "long ints", a reading machine with 32-bit C "long
  ints" will yield an array with 64-bit integers.

- Be reverse engineered.  Datasets often live longer than the
  programs that created them.  A competent developer should be
  able to create a solution in his preferred programming language to
  read most NPY files that he has been given without much
  documentation.

- Allow memory-mapping of the data.

- Be read from a filelike stream object instead of an actual file.
  This allows the implementation to be tested easily and makes the
  system more flexible.  NPY files can be stored in ZIP files and
  easily read from a ZipFile object.

- Store object arrays.  Since general Python objects are
  complicated and can only be reliably serialized by pickle (if at
  all), many of the other requirements are waived for files
  containing object arrays.  Files with object arrays do not have
  to be mmapable since that would be technically impossible.  We
  cannot expect the pickle format to be reverse engineered without
  knowledge of pickle.  However, one should at least be able to
  read and write object arrays with the same generic interface as
  other arrays.

- Be read and written using APIs provided in the numpy package
  itself without any other libraries.  The implementation inside
  numpy may be in C if necessary.

The format explicitly *does not* need to:

- Support multiple arrays in a file.  Since we require filelike
  objects to be supported, one could use the API to build an ad
  hoc format that supported multiple arrays.  However, solving the
  general problem and use cases is beyond the scope of the format
  and the API for numpy.

- Fully handle arbitrary subclasses of numpy.ndarray.  Subclasses
  will be accepted for writing, but only the array data will be
  written out.  A regular numpy.ndarray object will be created
  upon reading the file.  The API can be used to build a format
  for a particular subclass, but that is out of scope for the
  general NPY format.


Format Specification: Version 1.0
---------------------------------

The first 6 bytes are a magic string: exactly "\x93NUMPY".

The next 1 byte is an unsigned byte: the major version number of
the file format, e.g. \x01.

The next 1 byte is an unsigned byte: the minor version number of
the file format, e.g. \x00.  Note: the version of the file format
is not tied to the version of the numpy package.

The next 2 bytes form a little-endian unsigned short int: the
length of the header data HEADER_LEN.

The next HEADER_LEN bytes form the header data describing the
array's format.  It is an ASCII string which contains a Python
literal expression of a dictionary.  It is terminated by a newline
('\n') and padded with spaces ('\x20') to make the total length of
the magic string + 4 + HEADER_LEN be evenly divisible by 16 for
alignment purposes.

The dictionary contains three keys:

    "descr" : dtype.descr
        An object that can be passed as an argument to the
        numpy.dtype() constructor to create the array's dtype.

    "fortran_order" : bool
        Whether the array data is Fortran-contiguous or not.
        Since Fortran-contiguous arrays are a common form of
        non-C-contiguity, we allow them to be written directly to
        disk for efficiency.

    "shape" : tuple of int
        The shape of the array.

For repeatability and readability, this dictionary is formatted
using pprint.pformat() so the keys are in alphabetic order.

Following the header comes the array data.  If the dtype contains
Python objects (i.e. dtype.hasobject is True), then the data is
a Python pickle of the array.  Otherwise the data is the
contiguous (either C- or Fortran-, depending on fortran_order)
bytes of the array.  Consumers can figure out the number of bytes
by multiplying the number of elements given by the shape (noting
that shape=() means there is 1 element) by dtype.itemsize.

Format Specification: Version 2.0
---------------------------------

The version 1.0 format only allowed the array header to have a
total size of 65535 bytes.  This can be exceeded by structured
arrays with a large number of columns.  The version 2.0 format
extends the header size to 4 GiB.  `numpy.save` will automatically
save in 2.0 format if the data requires it, else it will always use
the more compatible 1.0 format.

The description of the fourth element of the header therefore has
become:

    The next 4 bytes form a little-endian unsigned int: the length
    of the header data HEADER_LEN.

Conventions
-----------

We recommend using the ".npy" extension for files following this
format.  This is by no means a requirement; applications may wish
to use this file format but use an extension specific to the
application.  In the absence of an obvious alternative, however,
we suggest using ".npy".

For a simple way to combine multiple arrays into a single file,
one can use ZipFile to contain multiple ".npy" files.  We
recommend using the file extension ".npz" for these archives.


Alternatives
------------

The author believes that this system (or one along these lines) is
about the simplest system that satisfies all of the requirements.
However, one must always be wary of introducing a new binary
format to the world.

HDF5 [2] is a very flexible format that should be able to
represent all of NumPy's arrays in some fashion.  It is probably
the only widely-used format that can faithfully represent all of
NumPy's array features.  It has seen substantial adoption by the
scientific community in general and the NumPy community in
particular.  It is an excellent solution for a wide variety of
array storage problems with or without NumPy.

HDF5 is a complicated format that more or less implements
a hierarchical filesystem-in-a-file.  This fact makes satisfying
some of the Requirements difficult.  To the author's knowledge, as
of this writing, there is no application or library that reads or
writes even a subset of HDF5 files that does not use the canonical
libhdf5 implementation.  This implementation is a large library
that is not always easy to build.  It would be infeasible to
include it in numpy.

It might be feasible to target an extremely limited subset of
HDF5.  Namely, there would be only one object in it: the array.
Using contiguous storage for the data, one should be able to
implement just enough of the format to provide the same metadata
that the proposed format does.  One could still meet all of the
technical requirements like mmapability.

We would accrue a substantial benefit by being able to generate
files that could be read by other HDF5 software.  Furthermore, by
providing the first non-libhdf5 implementation of HDF5, we would
be able to encourage more adoption of simple HDF5 in applications
where it was previously infeasible because of the size of the
library.  The basic work may encourage similar dead-simple
implementations in other languages and further expand the
community.

The remaining concern is about reverse engineerability of the
format.  Even the simple subset of HDF5 would be very difficult to
reverse engineer given just a file by itself.  However, given the
prominence of HDF5, this might not be a substantial concern.

In conclusion, we are going forward with the design laid out in
this document.  If someone writes code to handle the simple subset
of HDF5 that would be useful to us, we may consider a revision of
the file format.


Implementation
--------------

The version 1.0 implementation was first included in the 1.0.5 release of
numpy, and remains available.  The version 2.0 implementation was first
included in the 1.9.0 release of numpy.

Specifically, the file format.py in this directory implements the
format as described here.

    http://github.com/numpy/numpy/blob/master/numpy/lib/format.py


References
----------

[1] http://docs.python.org/lib/module-pickle.html

[2] http://hdf.ncsa.uiuc.edu/products/hdf5/index.html


Copyright
---------

This document has been placed in the public domain.

