%global build_branch master
%global pkg_name lld

%global build_repo https://github.com/llvm/llvm-project

%global maj_ver 11
%global min_ver 0
%global patch_ver 0

%define commit e9997cfb4d44e93cc65a29d1e1bb7451f418a7c7
%global commit_date 20200223

%global shortcommit %(c=%{commit}; echo ${c:0:7})

%global gitrel .%{commit_date}.git%{shortcommit}


Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0.1%{?gitrel}%{?dist}
Summary:	The LLVM Linker

License:	NCSA
URL:      https://llvm.org
Source0:  %{build_repo}/archive/%{commit}.tar.gz#/llvm-project-%{commit}.tar.gz

Patch0:		0001-CMake-Check-for-gtest-headers-even-if-lit.py-is-not-.patch
#Patch1:		0001-lld-Prefer-using-the-newest-installed-python-version.patch
#Patch2:		0001-Partial-support-of-SHT_GROUP-without-flag.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	llvm-devel = %{version}
BuildRequires:  llvm-static = %{version}
BuildRequires:  llvm-test = %{version}
BuildRequires:	ncurses-devel
BuildRequires:	zlib-devel
BuildRequires:	chrpath

# For make check:
BuildRequires:	python3-rpm-macros
BuildRequires:	python3-lit
BuildRequires:	llvm-googletest

%description
The LLVM project linker.

%package devel
Summary:	Libraries and header files for LLD

%description devel
This package contains library and header files needed to develop new native
programs that use the LLD infrastructure.

%package libs
Summary:	LLD shared libraries

%description libs
Shared libraries for LLD.

%prep
%autosetup -n llvm-project-%{commit}/%{name}

%build

mkdir %{_target_platform}
cd %{_target_platform}

%cmake .. \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=ON \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64
%else
	-DLLVM_LIBDIR_SUFFIX=
%endif

%make_build

%install
cd %{_target_platform}
%make_install

# Remove rpath
chrpath --delete %{buildroot}%{_bindir}/*
chrpath --delete %{buildroot}%{_libdir}/*.so*

%check
# armv7lhl tests disabled because of arm issue, see https://koji.fedoraproject.org/koji/taskinfo?taskID=33660162
#%ifnarch %{arm}
#make -C %{_target_platform} %{?_smp_mflags} check-lld
#%endif

%ldconfig_scriptlets libs

%files
%{_bindir}/lld*
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/wasm-ld

%files devel
%{_includedir}/lld
%{_libdir}/liblld*.so

%files libs
%{_libdir}/liblld*.so.*

%changelog
* Sat Nov 02 2019 Mihai Vultur <xanto@egaming.ro>
- Now that they have migrated to github, change to official source url.

* Sun Oct 06 2019 Mihai Vultur <xanto@egaming.ro>
- Architecture specific builds might run asynchronous.
- This might cause that same package build for x86_64 will be different when
-  built for i686. This is problematic when we want to install multilib packages. 
- Convert the specfile to template and use it to generate the actual script.
- This will prevent the random failues and mismatch between arch versions.

* Sun Jul 14 2019 Mihai Vultur <xanto@egaming.ro>
- Implement some version autodetection to reduce maintenance work.
- Based on spec files from 'GloriousEggroll' and 'che' coprs.
