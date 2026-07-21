{
  lib,
  makeWrapper,
  ncurses,
  python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "pipes-sh-python";
  version = "2.0.0";
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
    wrapProgram "$out/bin/pipes.sh" \
      --prefix TERMINFO_DIRS : "${ncurses}/share/terminfo"
  '';

  installCheckPhase = ''
    runHook preInstallCheck
    test -x "$out/bin/pipes.sh"
    test -f "$out/share/man/man6/pipes.sh.6"
    "$out/bin/pipes.sh" --help >/dev/null
    test "$("$out/bin/pipes.sh" --version)" = "pipes.sh 2.0.0"
    "$out/bin/pipes.sh" --self-test
    python -c 'import pipes_sh; assert pipes_sh.VERSION == "2.0.0"'
    find "$out" -type f -exec sha256sum {} + | sort > "$TMPDIR/before"
    "$out/bin/pipes.sh" --help >/dev/null
    "$out/bin/pipes.sh" --version >/dev/null
    "$out/bin/pipes.sh" --self-test >/dev/null
    find "$out" -type f -exec sha256sum {} + | sort > "$TMPDIR/after"
    cmp "$TMPDIR/before" "$TMPDIR/after"
    runHook postInstallCheck
  '';

  meta = {
    description = "Unofficial Python rewrite of the pipes.sh terminal screensaver";
    homepage = "https://github.com/xnixjoyer/Pipes";
    license = lib.licenses.mit;
    mainProgram = "pipes.sh";
    platforms = lib.platforms.linux;
  };
}
