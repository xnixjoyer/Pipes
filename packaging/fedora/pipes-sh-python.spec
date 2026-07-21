Name:           pipes-sh-python
Version:        3.0.0
Release:        1%{?dist}
Summary:        Pipes terminal screensaver, independently rewritten in Python
License:        MIT
URL:            https://github.com/xnixjoyer/Pipes
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
Requires:       ncurses-base
Provides:       pipes = %{version}-%{release}

%description
An unofficial, independently maintained Python rewrite of the classic pipes.sh
terminal screensaver. The installed public command is pipes; no pipes.sh alias is shipped.

%prep
%autosetup -n Pipes-%{version}

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
%{_bindir}/pipes
%{_mandir}/man6/pipes.6*

%changelog
* Tue Jul 21 2026 xnixjoyer <Error5634@proton.me> - 3.0.0-1
- Rename the installed command to pipes and add the pipes(6) manual
