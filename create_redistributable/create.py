#!/usr/bin/env python
import os, sys, argparse, shutil, platform, subprocess, tempfile

### Package Maker location (default on OS X)
_package_maker = '/Applications/PackageMaker.app/Contents/MacOS/PackageMaker'


class OSArch:
  def __init__(self):
    mac_version_to_name = {'10.9' : 'mavericks',
                           '10.10' : 'yosemite',
                           '10.11' : 'elcapitan'}
    self.uname = platform.platform()
    if self.uname.upper().find('DARWIN') != -1:
      self.system = 'darwin'
      self.release = mac_version_to_name['.'.join(platform.mac_ver()[0].split('.')[:-1])]
      self.version = platform.mac_ver()[0]
    else:
      # macintosh above is such a pain aint it
      self.system, self.version, self.release = platform.linux_distribution()
    self.temp_dir = tempfile.mkdtemp()

class DEB:
  """
Class for building Debian based packages
"""
  def __init__(self, args):
    self.args = args
    self.arch = OSArch()

  def prepare_area(self):
    return prepare_area(self.args, self.arch)

  def create_tarball(self):
    return True

  def create_redistributable(self):
    return True
  def commit_version_change(self):
    return True

class RPM:
  """
Class for building RedHat based packages
"""
  def __init__(self, args):
    self.args = args
    self.arch = OSArch()

  def prepare_area(self):
    return prepare_area(self.args, self.arch)

  def create_tarball(self):
    return True

  def create_redistributable(self):
    return True
  def commit_version_change(self):
    return True


class PKG:
  """
Class for building Macintosh Packages
"""
  def __init__(self, args):
    self.args = args
    self.arch = OSArch()
    self.redistributable_version = self._get_build_version()

  def _get_build_version(self):
    # Increment our redistributable version
    new_version += 1
    return new_version

  def prepare_area():
    if prepare_area(self.args, self.arch):
      # Iterate through all files in the template pmdoc directory and modify version specs
      for directory, directories, files in os.walk(os.path.join(self.arch.temp_dir, '-'.join([self.arch.system, self.arch.version])) + 'OSX.pmdoc')):
        for xml_file in files:
          tmp_file = open(os.path.join(self.arch.temp_dir, '.'.join([self.arch.system, self.arch.version]) + 'OSX.pmdoc', xml_file), 'r')
          xml_string = tmp_file.read()
          tmp_file.close()
          xml_string = xml_string.replace('<MAC_VERSION>', self.arch.version)
          xml_string = xml_string.replace('<REDISTRIBUTABLE_FILE>', self.args.redistributable_name)
          tmp_file = open(os.path.join(self.args.base_path, '.'.join([self.args.major, self.args.minor]) + 'OSX.pmdoc', xml_file), 'w')
          tmp_file.write(xml_string)
          tmp_file.close()

      # Iterate through the all control files that redistributable package uses during installation and
      # make some path/version specific changes based on machine type
      for html_file in ['README_Panel.html', 'Welcome_Panel.html', 'cleanup_post.sh', 'payload_post.sh', 'common_post.sh', 'environment_post.sh']:
        tmp_file = open(os.path.join(self.args.base_path, '.'.join([self.args.major, self.args.minor]), 'OSX', html_file), 'r')
        html_str = tmp_file.read()

        # If we are only building a package for OS X El Capitan (10.11), set a special
        # switch that allows the installer to create a symbolic link to our openMP
        # implementation (DYLD_LIBRARY_PATH issue)
        if html_file == 'common_post.sh' and self.arch.version.find('10.11') != -1:
          html_str = html_str.replace('<BOOL>', '1')
        else:
          html_str = html_str.replace('<BOOL>', '0')

        html_str = html_str.replace('<PACKAGES_DIR>', self.args.packages_dir)
        html_str = html_str.replace('<REDISTRIBUTABLE_VERSION>', 'Package version: ' + str(self.args.redistributable_version))
        tmp_file = open(os.path.join(self.args.base_path, '.'.join([self.args.major, self.args.minor]), html_file), 'w')
        tmp_file.write(html_str)
        tmp_file.close()
      return True
    else:
      return False

  def create_tarball():
    print 'Building tarball. This step can take a while...'
    os.chdir(self.args.packages_dir)
    try:
      shutil.make_archive(os.path.join(self.args.base_path, '.'.join([self.args.major, self.args.minor]), 'payload'), 'gztar', '.')
      print 'Tarball created'
    except os.error, err:
      print 'there was an error building tarball:', err
      return False
    return True

  def create_redistributable():
    os.chdir(self.args.base_path)
    print 'Building redistributable package. This step can also take some time...'
    package_builder = subprocess.Popen([self.args.package_maker, '--doc', os.path.join(self.args.base_path, str(self.args.major) + '.' + str(self.args.minor) + '.pmdoc')],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=False)

    results = package_builder.communicate()
    if len(results[1]) >= 1:
      print 'There was error building the redistributable package using PackageMaker:\n\n', results[1]
      return False
    else:
      return True

  def commit_version_change():
    version = 'something incremental'
    return version



def prepare_area(args, arch):
  try:
    # Create our template directory
    shutil.copytree(os.path.join(args.relative_path, args.package_type), os.path.join(arch.temp_dir, '-'.join([arch.system, arch.version]))), symlinks=False, ignore=None)
  except os.error, err:
    print 'could not copy template build project:', err
    return False
  return True

def verifyArgs(args):
  return args

def parseArguments(args=None):
  parser = argparse.ArgumentParser(description='Create Redistributable Package')
  parser.add_argument('-p', '--packages-dir', help='Directory where you installed everything to (/opt/moose)')
  parser.add_argument('--package-type', help='Specify type of package to build. Valid values: deb rpm pkg')
  parser.add_argument('-f', '--force', action='store_const', const=True, default=False, help='Overwrites previous redistributable package build attempt')
  return verifyArgs(parser.parse_args(args))

if __name__ == '__main__':
  args = parseArguments()
