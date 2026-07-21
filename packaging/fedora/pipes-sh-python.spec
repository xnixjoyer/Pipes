Name:           pipes-sh-python
Version:        2.0.0
Release:        1%{?dist}
Summary:        Unofficial Python rewrite of the pipes.sh terminal screensaver
License:        MIT
URL:            https://github.com/xnixjoyer/Pipes
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
Requires:       ncurses-base
Provides:       pipes.sh = %{version}-%{release}
Conflicts:      pipes-sh

%description
An unofficial, independently maintained Python rewrite of the classic pipes.sh
terminal screensaver. The public command remains pipes.sh for compatibility.

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pipes_sh

%check
%{python3} -m compileall -q pipes_sh.py tests
%{python3} -m unittest discover -s tests -v
%{python3} pipes_sh.py --self-test
%{python3} -O pipes_sh.py --self-test

%files -f %{pyproject_files}
%license LICENSE
%{_bindir}/pipes.sh
%{_mandir}/man6/pipes.sh.6*

%changelog
* Tue Jul 21 2026 xnixjoyer <Error5634@proton.me> - 2.0.0-1
- Initial package for the independent Python rewrite
