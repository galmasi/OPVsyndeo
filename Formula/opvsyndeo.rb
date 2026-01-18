class Opvsyndeo < Formula
  desc "macOS toolbar for pre-programmed sshuttle sessions"
  homepage "https://github.com/galmasi/OPVsyndeo"
  url "https://github.com/galmasi/OPVsyndeo/archive/refs/heads/main.tar.gz"
  version "0.1.0"
  sha256 "" # Will be calculated on first release
  license ""

  depends_on "python@3"
  depends_on "sshuttle"

  def install
    python3 = "python3"
    venv = virtualenv_create(libexec, python3)
    
    # Install Python dependencies
    venv.pip_install "rumps", "py2app", "requests", "packaging"

    # Install the application files
    libexec.install Dir["*.py"]
    libexec.install "icons"
    libexec.install "setup.py" if File.exist?("setup.py")
    
    # Create a wrapper script
    (bin/"opvsyndeo").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python3" "#{libexec}/OPVsyndeo.py" "$@"
    EOS
    chmod 0755, bin/"opvsyndeo"
  end

  def caveats
    <<~EOS
      OPVsyndeo is a menu bar application. To run it:
        opvsyndeo

      Configuration file location:
        ~/Library/Application Support/OPVsyndeo/OPVsyndeo.json

      Note: sshuttle requires sudo privileges. OPVsyndeo will guide you
      through the setup on first run.
    EOS
  end

  test do
    # Test that the script can be imported
    system "#{libexec}/bin/python3", "-c", "import sys; sys.path.insert(0, '#{libexec}'); import OPVsyndeo"
  end
end
