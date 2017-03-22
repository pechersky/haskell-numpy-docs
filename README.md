haskell-numpy-docs
------------------

This repo provides the docs with which one can compare how use Haskell (and
associated libraries) in the same way one would use the Python numerical library
[numpy][numpy]. A contribution of the [DataHaskell][datahaskell] project.

[numpy]: http://www.numpy.org
[datahaskell]: http://www.datahaskell.org/

Structure
=========

The `numpy` docs are provided as a submodule, pointing to the [numpy repo][numpy git].
Specifically, we care about the `docs` there.

The examples are in the `src` directory, grouped by the docs page that they are
associated with. Each docs page can have a different library provide examples.
Each library should get its own `hs` file. For example, there is a
[src/quickstart/hmatrix.hs](src/quickstart/hmatrix.hs) for the [HMatrix][hmatrix git] version of the numpy
quickstart docs.

The actual docs pages are built using [Sphinx][sphinx docs], a Python
documentation generator. It uses an `rst` format. To write docs based on the
examples you wrote, use the [sphinx-tabs][sphinx tabs git] and the specially
written `comparetabs` extensions. The docs `rst`s only require pointing to the
parent example documents, the lines that each example should pull in, and the
language of the example. For a good starting point, check out
[docs/quickstart.rst](docs/quickstart.rst).

[numpy git]: https://github.com/numpy/numpy/
[hmatrix git]: http://github.com/albertoruiz/hmatrix
[sphinx docs]: http://www.sphinx-doc.org/en/stable/
[sphinx tabs git]: https://github.com/djungelorm/sphinx-tabs

Developing
==========

Select the library you want to test. Add it to the [haskell-numpy-docs.cabal](haskell-numpy-docs.cabal)
file. Run `stack solver` to prepare the dependencies. Run `stack build` to
provide install the libraries.

There are some special things you might need to do to develop on Windows
machines. Specifically, you need to provide a BLAS implementation for HMatrix to
work. Check out `stack.yaml` for an example.

Testing
=======

You can write the Haskell examples to be valid Haskell. This is verifiable using
the [doctest][doctest git] library. To check an examples file, run a command
like `stack exec doctest src/quickstart/hmatrix.hs`, for example.

[doctest git]: https://github.com/sol/doctest

Building documentation
======================

Make sure the proper Python dependencies are installed using `pip install -r
requirements.txt`. To build the documentation, `cd` to the `docs` directory. Run
`make html`.

Contributing
============

File a PR with a new library, or new examples, or more idiomatic Haskell code.
File an issue for more in-depth discussion. Visit the [DataHaskell][datahaskell gitter]
channel and talk!

[datahaskell gitter]: https://gitter.im/dataHaskell/Lobby

---

Yakov Pechersky, 2017
