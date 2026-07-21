{
  lib,
  makeWrapper,
  ncurses,
  python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "pipes-sh-python";
  version = "3.0.0";
  pyproject = true;

  src = lib.cleanSource ../.;

  build-system = with python3Packages; [
    setuptools
    wheel
  ];

  nativeBuildInputs = [ makeWrapper ];
  nativeCheckInputs = [ python3Packages.build ];

  pythonImportsCheck = [ "pipes_sh" ];
  doCheck = true;
  doInstallCheck = true;

  checkPhase = ''
    runHook preCheck
    python -m compileall -q pipes_sh.py tests
    python -m unittest discover -s tests -v
    python pipes_sh.py --self-test
    python -O pipes_sh.py --self-test
    runHook postCheck
  '';

  postFixup = ''
    wrapProgram "$out/bin/pipes" \
      --prefix TERMINFO_DIRS : "${ncurses}/share/terminfo"
  '';

  installCheckPhase = ''
    runHook preInstallCheck
    test -x "$out/bin/pipes"
    test ! -e "$out/bin/pipes.sh"
    test -f "$out/share/man/man6/pipes.6" || test -f "$out/share/man/man6/pipes.6.gz"
    test ! -e "$out/share/man/man6/pipes.sh.6"
    test ! -e "$out/share/man/man6/pipes.sh.6.gz"
    "$out/bin/pipes" --help >/dev/null
    test "$("$out/bin/pipes" --version)" = "pipes 3.0.0"
    "$out/bin/pipes" --self-test
    python -c 'import pipes_sh; assert pipes_sh.VERSION == "3.0.0"'
    find "$out" -type f -exec sha256sum {} + | sort > "$TMPDIR/before"
    "$out/bin/pipes" --help >/dev/null
    "$out/bin/pipes" --version >/dev/null
    "$out/bin/pipes" --self-test >/dev/null
    find "$out" -type f -exec sha256sum {} + | sort > "$TMPDIR/after"
    cmp "$TMPDIR/before" "$TMPDIR/after"
    runHook postInstallCheck
  '';

  meta = {
    description = "Unofficial Python rewrite of the pipes.sh terminal screensaver";
    homepage = "https://github.com/xnixjoyer/Pipes";
    license = lib.licenses.mit;
    mainProgram = "pipes";
    platforms = lib.platforms.linux;
  };
}
