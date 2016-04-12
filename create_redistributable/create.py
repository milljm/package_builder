#!/usr/bin/env python
import os, sys, argparse, shlex, shutil, platform, subprocess, tempfile


class PackageCreator:
  """
Base class for building packages
"""
  def __init__(self, args):
    self.args = args
    self.base_name = _base_name
    self.uname = platform.platform()
    if self.uname.upper().find('DARWIN') != -1:
      self.system = 'darwin'
      self.version = '.'.join(platform.mac_ver()[0].split('.')[:-1])
      self.release = _mac_version_to_name[self.version]
    else:
      self.release, self.version, self.system = platform.linux_distribution()

    self.temp_dir = tempfile.mkdtemp()
    self.redistributable_version = self._get_build_version()
    self.redistributable_name = self.base_name + '_' + \
                                '-'.join([self.release, self.system, str(self.redistributable_version), 'x86_64']) + \
                                '.' + self.__class__.__name__.lower()

  def _get_build_version(self):
    if not os.path.exists(os.path.join(args.relative_path, self.__class__.__name__.lower(), self.version + '_build')):
      with open(os.path.join(args.relative_path, self.__class__.__name__.lower(), self.version + '_build'), 'w') as version_file:
        version_file.write('1')
        return '1'
    else:
      with open(os.path.join(args.relative_path, self.__class__.__name__.lower(), self.version + '_build'), 'r+') as version_file:
        new_version = int(version_file.read()) + 1
        version_file.truncate(0)
        version_file.seek(0)
        version_file.write(str(new_version))
        return new_version

  def clean_up(self):
    shutil.rmtree(self.temp_dir)

  def prepare_area(self):
    try:
      shutil.copytree(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), self.__class__.__name__.lower()), \
                      os.path.join(self.temp_dir, self.__class__.__name__.lower()), symlinks=True, ignore=None)
    except os.error, err:
      print err
      return False
    return True

  def create_tarball(self, tar_format='gztar'):
    try:
      print 'Creating tarball...'
      shutil.make_archive(os.path.join(self.temp_dir, self.__class__.__name__.lower(), 'payload'), tar_format, os.path.sep, self.args.packages_dir)
    except os.error, err:
      print err
      return False
    return True

  def create_redistributable(self):
    return True

  def commit_version_change(self):
    return True


class DEB(PackageCreator):
  """
Class for building Debian based packages
"""
  def prepare_area(self):
    create_template = PackageCreator.prepare_area(self)
    if create_template:
      for directory, directories, files in os.walk(os.path.join(self.temp_dir, 'deb/DEBIAN')):
        for xml_file in files:
          with open(os.path.join(self.temp_dir, 'deb/DEBIAN', xml_file), 'r+') as tmp_file:
            xml_string = tmp_file.read()
            tmp_file.truncate(0)
            tmp_file.seek(0)
            xml_string = xml_string.replace('<VERSION>', str(self.redistributable_version))
            xml_string = xml_string.replace('<PACKAGES_DIR>', self.args.packages_dir)
            tmp_file.write(xml_string)
      return True

  def create_tarball(self):
    # We need to copy files instead of using a tarball
    return self.copy_files()

  def copy_files(self):
    # Note: os.path.join drops previous paths when it encounters an absolute path
    # therefor we must trick it
    print 'Copying', self.args.packages_dir, 'to temp directory:', os.path.join(self.temp_dir, 'deb')
    os.makedirs(os.path.join(self.temp_dir, 'deb', *[x for x in os.path.dirname(self.args.packages_dir).split(os.sep)]))
    shutil.copytree(self.args.packages_dir,
                    os.path.join(self.temp_dir, 'deb', *[x for x in self.args.packages_dir.split(os.sep)]),
                    symlinks=True, ignore=None)
    return True

  def create_redistributable(self):
    print 'Building redistributable using dpkg... This can take a long time'
    os.chdir(self.temp_dir)
    package_builder = subprocess.Popen(['dpkg', '-b', 'deb'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    results = package_builder.communicate()
    if len(results[1]) >= 1:
      print 'There was error building the redistributable package using dpkg:\n\n', results[1]
      return False
    else:
      shutil.move(os.path.join(self.temp_dir, 'deb.deb'), os.path.join(self.args.relative_path, self.redistributable_name))
      print 'Redistributable built and available at:', os.path.join(self.args.relative_path, self.redistributable_name)
      return True

class RPM(PackageCreator):
  """
Class for building RedHat based packages
"""
  def _get_requirements(self):
    # RPM based distros have different package names for 'fortran'
    # and libX11-devel, so try and discover exactly which package
    # that actually is
    requirements = []
    our_requirements = ['gcc-*fortran', 'lib*11-devel']
    for index, item in enumerate(our_requirements):
      rpm_process = subprocess.Popen(['rpm', '-qa', item], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      rpm_results = rpm_process.communicate()[0]
      if rpm_results:
        our_requirements[index] = '-'.join(rpm_results.split('-')[:2])
        requirements.append(our_requirements[index])
    if len(requirements) == len(our_requirements):
      return requirements
    else:
      print '\nERROR: While building the list of dependencies the final redistributable will\n' \
        'require your users to install, I could not determine the correct package names\n' \
        'to add. The following is that list:\n\n\t', \
        ' '.join(set(our_requirements) - set(requirements)), \
        '\n\nThe unfortunate reason this happens, is due to the different ways each OS\n' \
        'using RPM as its package management system can name things differently, and\n' \
        'I am simply searching for the wrong package.\n\n' \
        'The easy fix, is to edit this script, find the line: "our_requirements = " and\n' \
        'modify the contents of that list to match the correct package installed using:\n\n\t' \
        'rpm -qa <package name>\n\n' \
        'Or... perhaps you really do not have the above packages installed... In which\n' \
        'case, simply installing that package and re-running this script will suffice.\n\n'
      return False

  def prepare_area(self):
    requirements = self._get_requirements()
    create_template = PackageCreator.prepare_area(self)
    if create_template and requirements:
      for directory, directories, files in os.walk(os.path.join(self.temp_dir, 'rpm/SPECS')):
        for xml_file in files:
          with open(os.path.join(self.temp_dir, 'rpm/SPECS', xml_file), 'r+') as tmp_file:
            xml_string = tmp_file.read()
            tmp_file.truncate(0)
            tmp_file.seek(0)
            xml_string = xml_string.replace('<VERSION>', str(self.redistributable_version))
            xml_string = xml_string.replace('<PACKAGES_DIR>', self.args.packages_dir)
            xml_string = xml_string.replace('<PACKAGES_BASENAME>', os.path.join(*[x for x in os.path.dirname(self.args.packages_dir).split(os.sep)]))
            xml_string = xml_string.replace('<PACKAGES_PARENT>', os.path.basename(self.args.packages_dir))
            xml_string = xml_string.replace('<REQUIREMENTS>', ' '.join(requirements))
            tmp_file.write(xml_string)
      for directory in ['BUILD', 'BUILDROOT', 'RPMS', 'SRPMS', 'SOURCES']:
        os.makedirs(os.path.join(self.temp_dir, 'rpm', directory))
      return True

  def create_tarball(self):
    tarball_results = PackageCreator.create_tarball(self, 'tar')
    if tarball_results:
      # move tarball into position inside the SOURCES directory
      shutil.move(os.path.join(self.temp_dir, 'rpm/payload.tar'), os.path.join(self.temp_dir, 'rpm/SOURCES', self.base_name + '.tar' ))
      return True

  def create_redistributable(self):
    print 'Building redistributable using rpmbuild... This can take a long time'
    os.chdir(self.temp_dir)
    package_builder = subprocess.Popen(['rpmbuild', '-bb',
                                        '--define=_topdir %s' % (os.path.join(self.temp_dir, 'rpm')),
                                        os.path.join(self.temp_dir, 'rpm/SPECS/moose-compilers.spec')],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    results = package_builder.communicate()
    if results[1].find('error') != -1:
      print 'There was error building the redistributable package using rpmbuild:\n\n', results[1]
      return False
    else:
      ### TODO
      # get major_version from spec file instead of arbitrarily setting it
      major_version = '1.1'
      shutil.move(os.path.join(self.temp_dir, 'RPMS/x86_64/',
                               '-'.join([self.base_name, major_version, self.version]) + '.x86_64.rpm'),
                  os.path.join(self.args.relative_path, self.redistributable_name))
      print 'Redistributable built and available at:', os.path.join(self.args.relative_path, self.redistributable_name)
      return True

class PKG(PackageCreator):
  """
Class for building Macintosh Packages
"""
  def prepare_area(self):
    create_template = PackageCreator.prepare_area(self)
    if create_template:
      for directory, directories, files in os.walk(os.path.join(self.temp_dir, 'pkg/OSX.pmdoc')):
        for xml_file in files:
          with open(os.path.join(self.temp_dir, 'pkg/OSX.pmdoc', xml_file), 'r+') as tmp_file:
            xml_string = tmp_file.read()
            tmp_file.truncate(0)
            tmp_file.seek(0)
            xml_string = xml_string.replace('<TEMP_DIR>', os.path.join(self.temp_dir, 'pkg/OSX'))
            xml_string = xml_string.replace('<MAC_VERSION>', self.version)
            xml_string = xml_string.replace('<REDISTRIBUTABLE_FILE>', self.redistributable_name)
            tmp_file.write(xml_string)

      # Iterate through the all control files that redistributable package uses during installation and
      # make some path/version specific changes based on machine type
      for html_file in ['README_Panel.html', 'Welcome_Panel.html', 'cleanup_post.sh', 'payload_post.sh', 'common_post.sh', 'environment_post.sh']:
        with open(os.path.join(self.temp_dir, 'pkg/OSX', html_file), 'r+') as tmp_file:
          html_str = tmp_file.read()
          tmp_file.truncate(0)
          tmp_file.seek(0)

          # If we are only building a package for OS X El Capitan (10.11), set a special
          # switch that allows the installer to create a symbolic link to our openMP
          # implementation (DYLD_LIBRARY_PATH issue)
          if html_file == 'common_post.sh' and self.version in _need_symbolic_link:
            html_str = html_str.replace('<BOOL>', '1')
          else:
            html_str = html_str.replace('<BOOL>', '0')

          html_str = html_str.replace('<PACKAGES_DIR>', self.args.packages_dir)
          html_str = html_str.replace('<REDISTRIBUTABLE_VERSION>', 'Package version: ' + str(self.redistributable_version))
          tmp_file.write(html_str)
      return True
    else:
      return False

  def create_redistributable(self):
    os.chdir(self.temp_dir)
    print 'Building redistributable using PackageMaker... This can take a long time'
    package_builder = subprocess.Popen([self.args.package_maker, '--doc', os.path.join(self.temp_dir, 'pkg/OSX.pmdoc')],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=False)

    results = package_builder.communicate()
    if len(results[1]) >= 1:
      print 'There was error building the redistributable package using PackageMaker:\n\n', results[1]
      return False
    else:
      shutil.move(os.path.join(self.temp_dir, 'osx.pkg'), os.path.join(self.args.relative_path, 'osx.pkg'))
      print 'Redistributable built! You should now sign the package using the following command:\n\n\t' \
          'productsign --sign "Developer ID Installer: BATTELLE ENERGY ALLIANCE, LLC (J2Y4H5G88N)"', \
          os.path.join(self.args.relative_path, 'osx.pkg'), \
          os.path.join(self.args.relative_path, self.redistributable_name), \
          '\n\nOnce complete, you can verify your package has been correctly signed by running the following command:\n\n\t', \
          'spctl -a -v --type install', os.path.join(self.args.relative_path, self.redistributable_name), \
          '\n\nFollowing that, your package (', os.path.join(self.args.relative_path, self.redistributable_name), \
          ')is ready for distribution'
      return True

def verifyArgs(args):
  fail = False

  # Try to determine package type, unless provided by the user
  if args.package_type is None:
    for package_type, arch_list in _pathetic_dict.iteritems():
      for arch in arch_list:
        if arch in platform.platform().upper():
          args.package_type = package_type
  else:
    for package_type, arch_list in _pathetic_dict.iteritems():
      if package_type.__name__ == args.package_type.upper():
        args.package_type = package_type

  # Package type is still none?
  if args.package_type is None:
    print 'Unable to determine package type. You must provide package type manually.\n' \
      'See --help for supported package types'
    fail = True

  # Add _package_maker to argparser namespace for easy access
  args.package_maker = _package_maker

  # Add absolute path location of execution script to
  # argparser namespace for easy access
  args.relative_path = os.path.abspath(os.path.dirname(sys.argv[0]))

  # Check to see if Package Maker even exists. Its the
  # point to this script after all
  if args.package_type == 'PKG' and not os.path.exists(args.package_maker):
    print '* Error: Package Maker does not appear to be installed in its default\n' \
      'location of:\n', args.package_maker, '\n'
    fail = True

  # Is what we are trying to distribute available?
  args.packages_dir = args.packages_dir.rstrip(os.path.sep)
  if args.packages_dir:
    if not os.path.exists(args.packages_dir):
      print '* Error: path provided:', args.packages_dir, 'not found'
      fail = True
  else:
    print '* Error: you need to supply a --packages-dir argument pointing\n' \
      'to where you installed everything to (--packages-dir /opt/moose)\n'
    fail = True

  if fail:
    print '\nPlease solve for the failures identified and re-run this script'
    sys.exit(1)
  return args

def parseArguments(args=None):
  parser = argparse.ArgumentParser(description='Create Redistributable Package')
  parser.add_argument('-p', '--packages-dir', help='Directory where you installed everything to (/opt/moose)')
  parser.add_argument('--package-type', help='Specify type of package to build. Valid values: deb rpm pkg')
  return verifyArgs(parser.parse_args(args))


### Base Name (name that preceeds all system and version information
#   when determining the name of the redistributable
# (_base_name_system-release-version_x86_64.deb)
_base_name = 'moose-environment'

### PackageMaker location (default on OS X)
_package_maker = '/Applications/PackageMaker.app/Contents/MacOS/PackageMaker'

### List of OS X versions that need a symbolic link to openmp
_need_symbolic_link = ['10.11', '10.12']

### A dictionary of class pointers corresponding to OS type
_pathetic_dict = { RPM : ['FEDORA', 'SUSE', 'CENTOS', 'RHEL'],
                   DEB : ['UBUNTU', 'MINT', 'DEBIAN', 'KUBUNTU'],
                   PKG : ['DARWIN']}

### Conversion of OS X version to release name
_mac_version_to_name = {'10.9'  : 'mavericks',
                        '10.10' : 'yosemite',
                        '10.11' : 'elcapitan',
                        '10.12' : 'fuji'}

if __name__ == '__main__':
  args = parseArguments()
  package = args.package_type(args)
  if package.prepare_area():
    if package.create_tarball():
      if package.create_redistributable():
        print 'Finished successfully. Removing temporary files..'
  package.clean_up()
