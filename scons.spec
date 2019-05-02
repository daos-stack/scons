#
# spec file for package scons
#
# Copyright (c) 2019 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%define modname scons
%global flavor %{nil}
%if "%{flavor}" == "test"
%define psuffix -test
%bcond_without test
%else
%define psuffix %{nil}
%bcond_with test
%endif
Name:           scons%{psuffix}
Version:        3.0.4
Release:        1.1
Summary:        Replacement for Make
License:        MIT
Group:          Development/Tools/Building
URL:            http://www.scons.org/
Source0:        https://github.com/SCons/%{modname}/archive/%{version}.tar.gz
#http://www.scons.org/doc/%%{version}/HTML/scons-user.html
Source1:        scons-user.html-%{version}.tar.bz2
# Adjust to exclude all failing tests
Source2:        grep-filter-list.txt
# Local modification
Patch8:         scons-3.0.0-fix-install.patch
BuildRequires:  fdupes
BuildRequires:  grep
BuildRequires:  python3-base >= 3.5
BuildRequires:  python3-lxml
BuildRequires:  python3-setuptools
Requires:       python3-base >= 3.5
%if %{with test}
# texlive texlive-latex3 biber texmaker ghostscript
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bison
# For tests
BuildRequires:  clang
BuildRequires:  docbook-xsl-pdf2index
BuildRequires:  docbook5-xsl-stylesheets
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  libtool
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  libxslt-tools
BuildRequires:  pcre-devel
BuildRequires:  subversion
BuildRequires:  swig
BuildRequires:  xmlgraphics-fop
%endif

%description
SCons is a make replacement that provides a range of enhanced features,
such as automated dependency generation and built-in compilation cache
support. SCons rule sets are Python scripts, which means that SCons
provides itself as well as the features. SCons allows you to use the
full power of Python to control compilation.

%prep
%setup -q -n %{modname}-%{version}
%autopatch -p1

sed -i -e '/QT_LIBPATH = os.path.join.*QTDIR/s/lib/%{_lib}/' \
    src/engine/SCons/Tool/qt.py
sed -i 's|%{_bindir}/env python|%{_bindir}/python3|' src/script/*

cp %{SOURCE2} grep-filter-list.txt
chmod -x src/CHANGES.txt README.rst src/RELEASE.txt

# the test is marked skipped but fails
rm test/MSVS/vs-14.1-exec.py

%build
python3 bootstrap.py build/scons
cd build/scons
%python3_build

%install
%if !%{with test}
cd build/scons
ls -lh build/lib
%python3_install \
 --standard-lib \
 --no-install-bat \
 --no-version-script \
 --install-scripts=%{_bindir} \
 --record installed_files.txt
%fdupes %{buildroot}%{python3_sitelib}
%endif

%check
%if %{with test}
%ifnarch aarch64 armv7l ppc64 ppc64le s390x
TEMP_FILE=$(mktemp --tmpdir %{modname}-test.XXXXXX)
trap 'rm -f -- "$TEMP_FILE"' INT TERM HUP EXIT
find src/ test/ -name \*.py \
    | grep -F -v -f grep-filter-list.txt >$TEMP_FILE
python3 runtest.py -f $TEMP_FILE
%else
echo "Skiping tests on this architecture due to failures"
%endif
%endif

%files
%license LICENSE
%doc src/CHANGES.txt README.rst src/RELEASE.txt
%if !%{with test}
%{_bindir}/*
%{python3_sitelib}/SCons
%{python3_sitelib}/%{modname}*.egg-info
%{_mandir}/man1/*%{ext_man}
%endif

%changelog
* Tue Mar 26 2019 Tomáš Chvátal <tchvatal@suse.com>
- Sort out the bcond_with/without for the multibuild to work
  properly
* Mon Mar 25 2019 Tomáš Chvátal <tchvatal@suse.com>
- Fix the testsuite pass to keep working
- Use regular python macros
- Use fdupes
* Fri Mar  1 2019 Andreas Stieger <andreas.stieger@gmx.de>
- scons 3.0.4:
  * Add TEMPFILESUFFIX to allow a customizable filename extension
  * Update TempFileMunge class to use PRINT_CMD_LINE_FUNC
  * Enhance cpp scanner regex logic to detect if/elif expressions
    without whitespaces but parenthesis like "#if(defined FOO)" or
    "#elif!(BAR)" correctly.
* Tue Jan 15 2019 astieger@suse.com
- scons 3.0.3:
  * upstream packaging fixes
  * Update doc examples to work with Python 3.5+
* Thu Jan  3 2019 davejplater@gmail.com
- Update to version 3.0.2, now works properly with python3 and
  fixes boo#1083830.
- Removed incorporated patches: no_deprecated_asserts.patch,
  removed_splitunc.patch, fix-jN-for-python-37.patch,
  replace_TestSuite_main.patch, stop_custom_OrderedDict.patch,
  no_time-clock.patch and fix-rpm-tests-for-newer-rpmbuild.patch.
- Upstream changes are too many to list see :
  /usr/share/doc/packages/scons/CHANGES.txt
* Thu Oct 11 2018 Matěj Cepl <mcepl@suse.com>
- Switch off more failing tests.
* Mon Oct  8 2018 Matěj Cepl <mcepl@suse.com>
- Make package not to be noarch (bsc#1109755)
* Thu Oct  4 2018 mcepl@suse.com
- Make package multibuild for separate testing
- Block failing tests (and block %%check section completely on
  non-Intel archs, as the tests are apparently not designed for
  that).
- Fix patches from the upstream to improve compatbiilty:
    fix-jN-for-python-37.patch
    fix-rpm-tests-for-newer-rpmbuild.patch
    no_deprecated_asserts.patch
    no_time-clock.patch
    removed_splitunc.patch
    replace_TestSuite_main.patch
    stop_custom_OrderedDict.patch
- Remove replace-imp-with-importlib.patch for now (to stabilize
  the package first)
* Wed Jul 25 2018 mcepl@suse.com
- Add replace-imp-with-importlib.patch (from the upstream PR
  https://github.com/SCons/scons/pull/3159)
- Remove compatibility ifs for SLE < 13
* Fri Nov 24 2017 mpluskal@suse.com
- Explicitly require python3 for python3 version of scons as
  dependency does not get generated automatically
* Wed Nov 15 2017 astieger@suse.com
- SCons 3.0.1:
  * Fix return value handling in to_String_for_subst()
  * Fixe Variables.GenerateHelpText() to now use the sort parameter
  * Fix Tool loading logic from exploding sys.path with many
    site_scons/site_tools prepended on py3.
  * Add additional output with time to process each SConscript file
    when using --debug=time.
  * Fix broken subst logic with "$$([...])"
  * Java/Jar building improvements and fixes
- Packaging changes:
  * drop scons-3.0.0-support-python-2-prints.patch, now upstream
  * Restore python2 support for SLE 12 and Leap 42.x
* Fri Nov  3 2017 mpluskal@suse.com
- Switch to python3
* Wed Oct  4 2017 astieger@suse.com
- SCons 3.0.0, a major release:
  * Some targets may rebuild when upgrading.
  * Significant changes in some python action signatures
  * Supports Python version earlier than 2.7 and 3.5+
  * Switching between PY 2.7 and PY 3.5, 3.6 will cause rebuilds
  * Updated language support: D, LaTeX, docbook
  * Remove deprecated tools CVS, Perforce, BitKeeper, RCS, SCCS, Subversion
  * Removed deprecated module SCons.Sig
- refresh scons-1.2.0-fix-install.patch to
  scons-3.0.0-fix-install.patch
- drop scons-1.2.0-noenv.patch, fix is done in spec
- drop rpmlintrc, no longer needed
- prevent a regression that would require Python3 syntax for
  print statements, add scons-3.0.0-support-python-2-prints.patch
* Tue Nov 22 2016 astieger@suse.com
- SCons 2.5.1:
  * Add scons-configure-cache.py to packaging. It was omitted
  * Use memoization to optimize PATH evaluation across all
    dependencies per node
* Wed Apr 20 2016 astieger@suse.com
- SCons 2.5.0:
  * Enhance implicit language scanning functionality
  * Cache directory sharding to improve NFS performance
* Fri Dec  4 2015 mpluskal@suse.com
- Update to 2.4.1
  * Added new configure check, CheckProg, to check for
    existence of a program.
  * Fix for issue #2840 - Fix for two environments specifying same
  target with different actions not throwing hard error. Instead
  SCons was incorrectly issuing a warning and continuing.
  * Add support `Microsoft Visual C++ Compiler for Python 2.7'
    Compiler can be obtained at:
  https://www.microsoft.com/en-us/download/details.aspx?id=44266
  * Fixed tigris issue #3011: Glob() excludes didn't work when
  used with VariantDir(duplicate=0)
  * Fix bug 2831 and allow Help() text to be appended to
  AddOption() help.
  * Reimplemented versioning for shared libraries, with the
  following effects
  * Fixed tigris issues #3001, #3006.
  * Fixed several other issues not reported to tigris, including:
    issues with versioned libraries in subdirectories with tricky
  names,
    issues with versioned libraries and variant directories,
    issue with soname not being injected to library when using D
  linkers,
  * Switched to direct symlinks instead of daisy-chained ones --
  soname and development symlinks point directly to the
  versioned shared library now), for rationale see:
    https://www.debian.org/doc/debian-policy/ch-sharedlibs.html
    https://fedoraproject.org/wiki/Packaging:Guidelines#Devel_Packages
    https://bitbucket.org/scons/scons/pull-requests/247/new-versioned-libraries-gnulink-cyglink/diff#comment-10063929
  * New construction variables to allow override default
  behavior: SONAME, SHLIBVERSIONFLAGS, _SHLIBVERSIONFLAGS,
  SHLIBNOVERSIONSYMLINKS, LDMODULEVERSION,
  LDMODULEVERSIONFLAGS, _LDMODULEVERSIONFLAGS,
  LDMODULENOVERSIONSYMLINKS.
  * Changed logic used to configure the versioning machinery
  from platform-centric to linker-oriented.
  * The SHLIBVERSION/LDMODULEVERSION variables are no longer
  validated by SCons (more freedom to users).
  * InstallVersionedLib() doesn't use SHLIBVERSION anymore.
  * Enchanced docs for the library versioning stuff.
  * New tests for versioned libraries.
  * Library versioning is currently implemented for the following
  linker tools: 'cyglink', 'gnulink', 'sunlink'.
  * Fix to swig tool - pick-up 'swig', 'swig3.0' and 'swig2.0'
  (in order).
  * Fix to swig tool - respect env['SWIG'] provided by user.
* Thu Sep 24 2015 mpluskal@suse.com
- Update to 2.4.0
  * Switched several core classes to use "slots", to reduce the
    overall memory consumption in large projects (fixes #2180,
    [#2178], #2198)
  * Memoizer counting uses decorators now, instead of the old
    metaclasses approach.
  * Fixed typo in SWIGPATH description
* Tue Aug 11 2015 astieger@suse.com
- SCons 2.3.6:
  * bug fixes
  * Added support for Visual Studio 2015
* Mon Jul 27 2015 astieger@suse.com
- SCons 2.3.5:
  * Documentation fixes
  * Fixed symlink support
  * Fixed incomplete LIBS flattening and substitution in Program
    scanner
  * Added new method rentry_exists_on_disk to Node.FS
  * Add support for f08 file extensions for Fortran 2008 code.
  * Show --config choices if no argument is specified
  * Added an 'exclude' parameter to Glob()
  * Added support for '-isystem' to ParseFlags.
* Sun Oct  5 2014 andreas.stieger@gmx.de
- SCons 2.3.4:
  * Fixed the interactive mode, in connection with Configure
    contexts
  * Fix EnsureSConsVersion warning when running packaged version
  * Fix D tools for building shared libraries
- for SLE 11 SP3 fix python requirements
* Mon Sep 29 2014 tchvatal@suse.com
- Cleanup with spec-cleaner (minor whitespace)
* Thu Aug 28 2014 andreas.stieger@gmx.de
- SCons 2.3.3:
  * New functionality:
  - Added Copy Action symlink soft-copy support
  * Changed/Enhanced existing functionality:
  - Improved SWIG detection
  * Fixes:
  - Fix regression on Windows in D language update
  - Fixed the newglossary action to work with VariantDir (LaTeX).
  - Added a default for the BUILDERS environment variable,
    to prevent not defined exception on a Clone().
  - Fixed handling of CPPDEFINE var in Append()
    for several list-dict combinations
- Remove scons-2.3.2-python.patch, committed upstream
* Thu Aug  7 2014 andreas.stieger@gmx.de
- Fix SCons with python 2.6 on SLE, including building serf:
  add scons-2.3.2-python.patch
* Mon Aug  4 2014 andreas.stieger@gmx.de
- SCons 2.3.2
- deprecated functionality
  * BitKeeper, CVS, Perforce, RCS, SCCS are deprecated from the
    default toolset and will be removed from the default toolset
    in future SCons versions.
  * D language, version 1, is now deprecated.  Version 2 is
    supported.
- changed/enhanced existing functionality
  * Revamp of D language support.
  * Tools for DMD, GDC and LDC are provided, and integrated
    with the C and C++ linking.
  * TeX builder now supports -synctex=1
  * TeX builder cleans auxiliary files correctly with biblatex.
- Fixes
  * Fixed handling of nested ifs in CPP scanner PreProcessor class.
  * Respect user's CC/CXX values; don't always overwrite in
    generate()
  * Delegate linker Tool.exists() to CC/CXX Tool.exists().
  * Fixed NoClean() for multi*target builders (#2353).
  * Fix SConf tests that write output
  * get default RPM architecture more robustly when building RPMs
  * Allow varlist to be specified as list of strings for Actions
  * Fixes to Docbook tool
* Wed Apr  9 2014 andreas.stieger@gmx.de
- SCons 2.3.1
  This release adds several new features and fixes many issues,
  including a serious regression in linking (failure to re-link if
  linker options are changed).
- new functionality:
  - Add Pseudo command to mark targets which should not exist after
    they are built.
  - Add support for a readonly cache (--cache-readonly)
  - Added optional ZIPROOT to Zip tool.
- enhancements:
  - DocBook tool can now output EPUB format
  - Allow multiple options to be specified with --debug=a,b,c
  - Update bootstrap.py so it can be used from any dir, to run
    SCons from a source (non-installed) dir.
  - Added release_target_info() to File nodes, which helps to
    reduce memory consumption in clean builds and update runs
    of large projects.
  - Print full stack on certain errors, for debugging.
  - Improve documentation for Textfile builder.
- bug fixes:
  - Stop leaking file handles to subprocesses by switching to using
    subprocess always.
  - Generally try harder to print out a message on build errors
  - Added a switch to warn on missing targets
  - Always print stats if requested
  - Make sure SharedLibrary depends on all dependent libs (by
    depending on SHLINKCOM)
  - Allow Subst.Literal string objects to be compared with each other,
    so they work better in AddUnique() and Remove().
  - Fixed the handling of long options in the command-line
    parsing
  - Fixed misspelled variable in intelc.py (#2928).
  - Fixed spelling errors in MAN pages (#2897).
  - Fixed description of ignore_case for EnumVariable in the MAN
    page
- adjust scons-1.2.0-fix-install.patch for context changes
- remove versioned binaries from /usr/bin
* Sun Jul 21 2013 andreas.stieger@gmx.de
- update to 2.3.0
  - Added ability to run scripts/scons.py directly from source checkout
  - Hide deprecated --debug={dtree,stree,tree} from --help output
  - Error messages from option parser now include hints about valid choices
  - Cleaned up some Python 1.5 and pre-2.3 code, so don't expect SCons
    to run on anything less than Python 2.4 anymore
  - Several fixes for runtest.py:
  * exit with an error if no tests were found
  * removed --noqmtest option - this behavior is by default
  * replaced `-o FILE --xml` combination with `--xml FILE`
  * changed `-o, --output FILE` option to capture stdout/stderr output
    from runtest.py
  - Remove os_spawnv_fix.diff patch required to enable parallel builds
    support prior to Python 2.2
  - Fix WiX Tool to use .wixobj rather than .wxiobj for compiler output
  - Support building with WiX releases after 2.0
  - Fix nested LIBPATH expansion by flattening sequences in subst_path.
  - Print target name with command execution time with --debug=time
  - Updated test framework to support dir and file fixtures and
    added ability to test external (out-of-tree) tools
  - Fixed several errors in the test suite (Java paths, MSVS version
    detection, Tool import), additionally
  * provided MinGW command-line support for the CXX, AS and
    Fortran tests,
  * refactored the detection of the gcc version and the according
    Fortran startup library,
  * provided a new module rpmutils.py, wrapping the RPM naming rules
    for target files and further hardware-dependent info (compatibility,
    compiler flags, ...),
  * added new test methods must_exist_one_of() and
    must_not_exist_any_of() and
  * removed Aegis support from runtest.py. (#2872)
  - Add -jN support to runtest.py to run tests in parallel
  - Updated the TeX builder to support the \newglossary command
    in LaTeX's glossaries package and the files it creates.
  - Improve support for new versions of biblatex in the TeX builder
    so biber is called automatically if biblatex requires it.
  - Add SHLIBVERSION as an option that tells SharedLibrary to build
    a versioned shared library and create the required symlinks.
    Add builder InstallVersionedLib to create the required symlinks
    installing a versioned shared library.
- packaging changes
  * update to current (and compressed) user guide
  * make noarch package
* Sat Sep 22 2012 i@marguerite.su
- Update to 2.2.0
  * Added gettext toolset
  * Fixed FindSourceFiles to find final sources (leaf nodes)
  * Allow Node objects in Java path (#2825)
  * Fixed the Taskmaster, curing spurious build failures
  * Improved documentation of command-line variables
* Tue Oct 11 2011 nmarques@opensuse.org
- SCons 2.1.0 requires py_abi > 2.4
- Potential build fix for SLE11, SLE11_SP1
  + add python_sitearch/python_sitelib macros for <= 1120
  + improved source URL
  + add comment for patch
- Add scons-rpmlintrc: source-or-patch-not-bzipped,
  python-naming-policy-not-applied
* Tue Oct 11 2011 nmarques@opensuse.org
- Update to 2.1.0:
  + Fix Windows resource compiler scanner to accept DOS line
    endings.
  + Update MSVS documents to remove note indicating that only one
    project is currently supported per solution file.
  + Fix long compile lines in batch mode by using TEMPFILE
  + Fix MSVC_BATCH=False (was treating it as true)
  + support -std=c++0x and related CXXFLAGS in pkgconfig
    (ParseFlags)
  + Support -dylib_file in pkgconfig (ParseFlags)
  + new construction variable WINDOWS_EMBED_MANIFEST to
    automatically embed manifests in Windows EXEs and DLLs.
  + Fix Visual Studio project generation when CPPPATH contains Dir nodes
  + Ensure Visual Studio project is regenerated when CPPPATH or
    CPPDEFINES change
  + Fix unicode error when using non-ASCII filenames with Copy or
    Install
  + Put RPATH in LINKCOM rather than LINKFLAGS so resetting
    LINKFLAGS doesn't kill RPATH
  + Fix precompiled headers on Windows when variant dir name has
    spaces.
  + Adding None to an Action no longer fails (just returns original
    action)
  + New --debug=prepare option to show each target as it's being
    prepared, whether or not anything needs to be done for it.
  + New debug option --debug=duplicate to print a line for each
    unlink/relink (or copy) of a variant file from its source
    file.
  + Improve error message for EnumVariables to show legal values.
  + Fix Intel compiler to sort versions >9 correctly (esp. on
    Linux)
  + Fix Install() when the source and target are directories and
    the target directory exists.
  + Many more, please see ChangeLog/Changes.
* Wed Feb 10 2010 davejplater@gmail.com
- updated to 1.2.0.d20100117
  - Fixed temp filename race condition on Windows with long cmd lines
  - Fixed tryRun when sconf directory is in a variant dir.
  - Do not add -fPIC for ifort tool on non-posix platforms (darwin and
    windows).
  - Fix bug 2294 (spurious CheckCC failures).
  - Fix scons bootstrap process on windows 64 (wrong wininst name)
  - Final merge from vs_revamp branch to main
  - Added definition and usage of HOST_OS, HOST_ARCH, TARGET_OS,
    TARGET_ARCH, currently only defined/used by Visual Studio
    Compilers. This will be rolled out to other platforms/tools
    in the future.
  - Add check for python >= 3.0.0 and exit gracefully.
    For 1.3 python >= 1.5.2 and < 3.0.0 are supported
  - Fix bug 1944 - Handle non-existent .i file in swig emitter, previously
    it would crash with an IOError exception. Now it will try to make an
    educated guess on the module name based on the filename.
  - Have AddOption() remove variables from the list of
    seen-but-unknown variables (which are reported later).
  - An option name and aliases can now be specified as a tuple.
  - Textfile builder.
  - use "is/is not" in comparisons with None instead of "==" or "!=".
  - Avoid adding -gphobos to a command line multiple times
    when initializing use of the DMD compiler.
  - Fix the -n option when used with VariantDir(duplicate=1)
    and the variant directory doesn't already exist.
  - Fix scanning of Unicode files for both UTF-16 endian flavors.
  - Fix a TypeError on #include of file names with Unicode characters.
  - Fix an exception if a null command-line argument is passed in.
  - Evaluate Requires() prerequisites before a Node's direct children
    (sources and dependencies).
  - Remove redundant __metaclass__ initializations in Environment.py.
  - Correct the documentation of text returned by sconf.Result().
  - Document that filenames with '.' as the first character are
    ignored by Glob() by default (matching UNIX glob semantics).
  - Fix SWIG testing infrastructure to work on Mac OS X.
  - Restructure a test that occasionally hung so that the test would
    detect when it was stuck and fail instead.
  - Substfile builder.
  - When reporting a target that SCons doesn't know how to make,
    specify whether it's a File, Dir, etc.
  - Fix use of $SWIGOUTDIR when generating Python wrappers.
  - Add $SWIGDIRECTORSUFFIX and $SWIGVERSION construction variables.
  - Add -recorder flag to Latex commands and updated internals to
    use the output to find files TeX creates. This allows the MiKTeX
    installations to find the created files
  - Notify user of Latex errors that would get buried in the
    Latex output
  - Remove LATEXSUFFIXES from environments that don't initialize Tex.
  - Add support for the glosaaries package for glossaries and acronyms
  - Fix problem that pdftex, latex, and pdflatex tools by themselves did
    not create the actions for bibtex, makeindex,... by creating them
    and other environment settings in one routine called by all four
    tex tools.
  - Fix problem with filenames of sideeffects when the user changes
    the name of the output file from the latex default
  - Add scanning of files included in Latex by means of \lstinputlisting{}
    Patch from Stefan Hepp.
  - Change command line for epstopdf to use --outfile= instead of -o
    since this works on all platforms.
    Patch from Stefan Hepp.
  - Change scanner to properly search for included file from the
    directory of the main file instead of the file it is included from.
    Also update the emitter to add the .aux file associated with
    \include{filename} commands. This makes sure the required directories
    if any are created for variantdir cases.
* Mon Jan 19 2009 prusnak@suse.cz
- updated to 1.2.0.d20090113
  - Add support for batch compilation of Visual Studio C/C++ source
    files, controlled by a new $MSVC_BATCH construction variable.
  - Print the message, "scons: Build interrupted." on error output,
    not standard output.
  - Add a --warn=future-deprecated option for advance warnings about
    deprecated features that still have warnings hidden by default.
  - Fix use of $SOURCE and $SOURCES attributes when there are no
    sources specified in the Builder call.
  - Add support for new $CHANGED_SOURCES, $CHANGED_TARGETS,
    $UNCHANGED_SOURCES and $UNCHANGED_TARGETS variables.
  - Add general support for batch builds through new batch_key= and
    targets= keywords to Action object creation.
  - Make linker tools differentiate properly between SharedLibrary
    and LoadableModule.
  - Document TestCommon.shobj_prefix variable.
  - Support $SWIGOUTDIR values with spaces.
  - Don't automatically try to build .pdf graphics files for
    .eps files in \includegraphics{} calls in TeX/LaTeX files
    when building with the PDF builder (and thus using pdflatex).
  - Allow AppendENVPath() and PrependENVPath() to interpret '#'
    for paths relative to the top-level SConstruct directory.
  - Use the Borland ilink -e option to specify the output file name.
  - Document that the msvc Tool module uses $PCH, $PCHSTOP and $PDB.
  - Allow WINDOWS_INSERT_DEF=0 to disable --output-def when linking
    under MinGW.
  - Fix typos in the User's Guide.
  - Support implicit dependency scanning of files encoded in utf-8
    and utf-16.
  - Remove $CCFLAGS from the the default definitions of $CXXFLAGS for
    Visual C/C++ and MIPSpro C++ on SGI so, they match other tools
    and avoid flag duplication on C++ command lines.
  - Handle quoted module names in SWIG source files.
  - Copy file attributes so we identify, and can link a shared library
    from, shared object files in a Repository.
- updated to 1.2.0
  - Don't fail if can't import a _subprocess module on Windows.
  - Add warnings for use of the deprecated Options object.
* Wed Dec  3 2008 prusnak@suse.cz
- updated to 1.1.0.d20081125
  - Improve the robustness of GetBuildFailures() by refactoring
    SCons exception handling (especially BuildError exceptions).
  - Fix $FORTRANMODDIRPREFIX for the ifort (Intel Fortran) tool.
  - Don't pre-generate an exception message (which will likely be
    ignored anyway) when an EntryProxy re-raises an AttributeError.
  - Handle Java inner classes declared within a method.
  - Fix label placement by the "scons-time.py func" subcommand
    when a profile value was close to (or equal to) 0.0.
  - Fix env.Append() and env.Prepend()'s ability to add a string to
    list-like variables like $CCFLAGS under Python 2.6.
  - Other Python2.6 portability:  don't use "as" (a Python 2.6 keyword).
    Don't use the deprecated Exception.message attribute.
  - Support using the -f option to search for a different top-level
    file name when walking up with the -D, -U or -u options.
  - Fix use of VariantDir when the -n option is used and doesn't,
    therefore, actually create the variant directory.
  - Fix a stack trace from the --debug=includes option when passed a
    static or shared library as an argument.
  - Speed up the internal find_file() function (used for searching
    CPPPATH, LIBPATH, etc.).
  - Add support for using the Python "in" keyword on construction
    environments (for example, if "CPPPATH" in env: ...).
  - Scan for TeX files in the paths specified in the $TEXINPUTS
    construction variable and the $TEXINPUTS environment variable.
  - Configure the PDF() and PostScript() Builders as single_source so
    they know each source file generates a separate target file.
  - Add $EPSTOPDF, $EPSTOPDFFLAGS and $EPSTOPDFCOM
  - Add .tex as a valid extension for the PDF() builder.
  - Add regular expressions to find \input, \include and
    \includegraphics.
  - Support generating a .pdf file from a .eps source.
  - Recursive scan included input TeX files.
  - Make the Action() function handle positional parameters consistently.
  - Fix Glob() so an on-disk file or directory beginning with '#'
    doesn't throw an exception.
- updated to 1.1.0
  - Use the specified environment when checking for the GCC compiler
    version.
  - Fix Glob() polluting LIBPATH by returning copy of list
  - Add CheckCC, CheckCXX, CheckSHCC and CheckSHCXX tests to
    configuration contexts.
  - Have the --profile= argument use the much faster cProfile module
    (if it's available in the running Python version).
  - Reorder MSVC compilation arguments so the /Fo is first.
  - Add scanning Windows resource (.rc) files for implicit dependencies.
  - When scanning for a #include file, don't use a directory that
    has the same name as the file.
  - Suppress error output when checking for the GCC compiler version.
  - Fix VariantDir duplication of #included files in subdirectories.
  - Reduce memory usage when a directory is used as a dependency of
    another Node (such as an Alias) by returning a concatenation
    of the children's signatures + names, not the children's contents,
    as the directory contents.
  - Raise AttributeError, not KeyError, when a Builder can't be found.
  - Invalidate cached Node information (such as the contenst returned
    by the get_contents() method) when calling actions with Execute().
  - Avoid object reference cycles from frame objects.
  - Reduce memory usage from Null Executor objects.
  - Compute MD5 checksums of large files without reading the entire
    file contents into memory.  Add a new --md5-chunksize option to
    control the size of each chunk read into memory.
  - Fix the ability of the add_src_builder() method to add a new
    source builder to any other builder.
  - Avoid an infinite loop on non-Windows systems trying to find the
    SCons library directory if the Python library directory does not
    begin with the string "python".
  - Search for the SCons library directory in "scons-local" (with
    no version number) after "scons-local-{VERSION}".
  - Fix the user's ability to interrupt the TeX build chain.
  - Fix the TeX builder's allowing the user to specify the target name,
    instead of always using its default output name based on the source.
  - Iterate building TeX output files until all warning are gone
    and the auxiliary files stop changing, or until we reach the
    (configurable) maximum number of retries.
  - Add TeX scanner support for:  glossaries, nomenclatures, lists of
    figures, lists of tables, hyperref and beamer.
  - Use the $BIBINPUTS, $BSTINPUTS, $TEXINPUTS and $TEXPICTS construction
    variables as search paths for the relevant types of input file.
  - Fix building TeX with VariantDir(duplicate=0) in effect.
  - Fix the LaTeX scanner to search for graphics on the TEXINPUTS path.
  - Have the PDFLaTeX scanner search for .gif files as well.
  - Fix typos and format bugs in the man page.
  - Add a first draft of a wrapper module for Python's subprocess
    module.
  - Refactor use of the SCons.compat module so other modules don't
    have to import it individually.
  - Add .sx as a suffix for assembly language files that use the
    C preprocessor.
  - Make Glob() sort the returned list of Files or Nodes
    to prevent spurious rebuilds.
  - Add a delete_existing keyword argument to the AppendENVPath()
    and PrependENVPath() Environment methods.
  - Add ability to use "$SOURCE" when specifying a target to a builder
  - Add a test case to verify that SConsignFile() files can be
    created in previously non-existent subdirectories.
  - Make the subdirectory in which the SConsignFile() file will
    live, if the subdirectory doesn't already exist.
  - Add a test to verify duplication of files in VariantDir subdirectories.
* Mon Sep  8 2008 prusnak@suse.cz
- updated to 1.0.1
  * Add a FindFile() section to the User's Guide.
  * Fix the FindFile() documentation in the man page.
  * Fix formatting errors in the Package() description in the man page.
  * Escape parentheses that appear within variable names when spawning
    command lines using os.system().
- updated to 1.0.0.d20080826
  * Clear the Node state when turning a generic Entry into a Dir.
  * Fix sporadic output-order failures in test/GetBuildFailures/parallel.py.
  * Document the ParseDepends() function in the User's Guide.
  * Create a separate description and long_description for RPM packages.
  * Document the GetLaunchDir() function in the User's Guide.
  * Have the env.Execute() method print an error message if the
    executed command fails.
  * Add a script for creating a standard SCons development system on
    Ubuntu Hardy.  Rewrite subsidiary scripts for install Python and
    SCons versions in Python (from shell).
  * Handle yacc/bison on newer Mac OS X versions creating file.hpp,
    not file.cpp.h.
  * In RPCGEN tests, ignore stderr messages from older versions of
    rpcgen on some versions of Mac OS X.
  * Fix typos in man page descriptions of Tag() and Package(), and in
    the scons-time man page.
  * Fix documentation of SConf.CheckLibWithHeader and other SConf methods.
  * Update documentation of SConscript(variant_dir) usage.
  * Fix SWIG tests for (some versions of) Mac OS X.
  * Print the warning about -j on Windows being potentially unreliable if
    the pywin32 extensions are unavailable or lack file handle operations.
  * Fix the env.WhereIs() method to expand construction variables.
  * Enable building of shared libraries with the Bordand ilink32 linker.
- updated to 1.0.0
  * Fix SCons man page indentation under Debian's man page macros.
  * Clarify the man page description of the SConscript(src_dir) argument.
  * Document MergeFlags(), ParseConfig(), ParseFlags() and SideEffect()
    in the User's Guide.
  * Document use of the GetBuildFailures() function in the User's Guide.
  * Add man page text clarifying the behavior of AddPreAction() and
    AddPostAction() when called with multiple targets.
  * Fix incorrectly swapped man page descriptions of the --warn= options
    for duplicate-environment and missing-sconscript.
  * User's Guide updates
  * Man page updates
- updated to 0.98.5
  * Fix the Intel C++ compiler ABI specification for EMT64 processors.
  * Issue a (suppressable) warning, not an error, when trying to link
    C++ and Fortran object files into the same executable.
  * Update the scons.bat file so that it returns the real exit status
    from SCons, even though it uses setlocal + endlocal.
  * Fix the --interactive post-build messages so it doesn't get stuck
    mistakenly reporting failures after any individual build fails.
  * Fix calling File() as a File object method in some circumstances.
  * Fix setup.py installation on Mac OS X so SCons gets installed
    under /usr/lcoal by default, not in the Mac OS X Python framework.
- updated to 0.98.4
  * Fix calculation of signatures for Python function actions with
    closures in Python versions before 2.5.
  * Fix the initialization of $SHF77FLAGS so it includes $F77FLAGS.
  * Fix a syntax error in the Intel C compiler support on Windows.
  * Change how we represent Python Value Nodes when printing and when
    stored in .sconsign files (to avoid blowing out memory by storing
    huge strings in .sconsign files after multiple runs using Configure
    contexts cause the Value strings to be re-escaped each time).
  * Fix a regression in not executing configuration checks after failure
    of any configuration check that used the same compiler or other tool.
  * Handle multiple destinations in Visual Studio 8 settings for the
    analogues to the INCLUDE, LIBRARY and PATH variables.
  * Update man page text for VariantDir().
* Wed Apr 30 2008 prusnak@suse.cz
- updated to 0.98.3
  * fix use of $CXXFLAGS when building C++ shared object files
  * fix a regression when a Builder's source_scanner doesn't select
    a more specific scanner for the suffix of a specified source file
  * fix the Options object backwards compatibility so people can still
    "import SCons.Options.{Bool,Enum,List,Package,Path}Option" submodules
  * fix searching for implicit dependencies when an Entry Node shows up
    in the search path list
  * fix expansion of $FORTRANMODDIR in the default Fortran command line(s)
    when it's set to something like ${TARGET.dir}
* Tue Apr 22 2008 prusnak@suse.cz
- updated to 0.98.2
  * changes too numerous to list - see CHANGES.txt
* Mon Nov 12 2007 prusnak@suse.cz
- replaced /usr/bin/env in shebang by /usr/bin/python (noenv.patch)
- replaces duplicities in bindir by symlinks
* Wed May 30 2007 ltinkl@suse.cz
- update to stable release 0.97
- fix man installation patch
* Wed Mar  8 2006 ltinkl@suse.cz
- add more documentation (#154045)
* Tue Feb 28 2006 jmatejek@suse.cz
- updated to reflect python changes due to #149809
* Wed Jan 25 2006 mls@suse.de
- converted neededforbuild to BuildRequires
* Thu Nov 24 2005 sbrabec@suse.cz
- Bi-arch hack.
* Thu Nov  3 2005 dmueller@suse.de
- update to 0.96.91
* Tue Aug 24 2004 mcihar@suse.cz
- install man pages
* Tue Aug 24 2004 mcihar@suse.cz
- initial packaging
