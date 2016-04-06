#!/usr/bin/env python
import os, sys, argparse, shutil, platform, subprocess

### Location where the package templates will be created
# For now, this is a hard coded location. See README
# in current directory for reasons why
_base_path='/tmp/moose_compiler_package'

### Package Maker location (default on OS X)
_package_maker = '/Applications/PackageMaker.app/Contents/MacOS/PackageMaker'

### Dictionary of major version numbers to names.
# Unfortunately, platform does not report a friendly
# name so we must do something like this:
_version_to_name = {'10.9' : 'mavericks',
                    '10.10' : 'yosemite',
                    '10.11' : 'elcapitan'}

def prepare_area(args):
  # Delete previous build if it exists
  if os.path.exists(args.base_path):
    try:
      shutil.rmtree(args.base_path)
    except os.error, err:
      print 'could not remove previous build due to permissions:', err
      return False
    except:
      print 'a general error occured attempting to remove', args.base_path, err
      return False
  try:
    # Create our template, based on machine type
    shutil.copytree(os.path.join(args.relative_path, 'OSX'), os.path.join(args.base_path, '.'.join([args.major, args.minor])), symlinks=False, ignore=None)
  
    # Also include the PackageMaker document (.pmdoc)
    ### TODO, does shutil handle wildcards?
    shutil.copytree(os.path.join(args.relative_path, 'OSX.pmdoc'), os.path.join(args.base_path, '.'.join([args.major, args.minor]) + '.pmdoc'), symlinks=False, ignore=None)
  except os.error, err:
    print 'could not copy template build project:', err
    return False

  # Iterate through all files in the template pmdoc directory and modify version specifics
  for directory, directories, files in os.walk(os.path.join(args.base_path, '.'.join([args.major, args.minor]) + '.pmdoc')):
    for xml_file in files:
      tmp_file = open(os.path.join(args.base_path, '.'.join([args.major, args.minor]) + '.pmdoc', xml_file), 'r')
      xml_string = tmp_file.read()
      tmp_file.close()
      xml_string = xml_string.replace('<MAC_VERSION>', '.'.join([args.major, args.minor]))
      xml_string = xml_string.replace('<REDISTRIBUTABLE_FILE>', args.redistributable_name)
      tmp_file = open(os.path.join(args.base_path, '.'.join([args.major, args.minor]) + '.pmdoc', xml_file), 'w')
      tmp_file.write(xml_string)
      tmp_file.close()

  # Iterate through the all control files that redistributable package uses during installation and
  # make some path/version specific changes based on machine type
  for html_file in ['README_Panel.html', 'Welcome_Panel.html', 'cleanup_post.sh', 'payload_post.sh', 'common_post.sh', 'environment_post.sh']:
    tmp_file = open(os.path.join(args.base_path, '.'.join([args.major, args.minor]), html_file), 'r')
    html_str = tmp_file.read()

    # If we are only building a package for OS X El Capitan (10.11), set a special
    # switch that allows the installer to create a symbolic link to our openMP
    # implementation (DYLD_LIBRARY_PATH issue)
    if html_file == 'common_post.sh' and '.'.join([args.major, args.minor]) == '10.11':
      html_str = html_str.replace('<BOOL>', '1')
    else:
      html_str = html_str.replace('<BOOL>', '0')

    html_str = html_str.replace('<PACKAGES_DIR>', args.packages_dir)
    html_str = html_str.replace('<REDISTRIBUTABLE_VERSION>', 'Package version: ' + str(args.redistributable_version))
    tmp_file = open(os.path.join(args.base_path, '.'.join([args.major, args.minor]), html_file), 'w')
    tmp_file.write(html_str)
    tmp_file.close()
    
  return True

def create_tarball(args):
  print 'Building tarball. This step can take a while...'
  os.chdir(args.packages_dir)
  try:
    shutil.make_archive(os.path.join(args.base_path, '.'.join([args.major, args.minor]), 'payload'), 'gztar', '.')
    print 'Tarball created'
  except os.error, err:
    print 'there was an error building tarball:', err
    return False
  return True

def create_redistributable(args):
  os.chdir(args.base_path)
  print 'Building redistributable package. This step can also take some time...'
  package_builder = subprocess.Popen([args.package_maker, '--doc', os.path.join(args.base_path, str(args.major) + '.' + str(args.minor) + '.pmdoc')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=False)
  
  results = package_builder.communicate()
  if len(results[1]) >= 1:
    print 'There was error building the redistributable package using PackageMaker:\n\n', results[1]
    return False
  else:
    return True

def commit_version_change(args):
  version = 'something incremental'
  return version
  
def verifyArgs(args):
  fail = False
  # Add _package_maker to argparser namespace for easy access
  args.package_maker = _package_maker

  # Add _base_path to argparser namespace for easy access
  args.base_path = _base_path

  # Add absolute path location of execution script to
  # argparser namespace for easy access
  args.relative_path = os.path.abspath(os.path.dirname(sys.argv[0]))

  # Check to see if Package Maker even exists. Its the
  # point to this script after all
  if not os.path.exists(args.package_maker):
    print '* Error: Package Maker does not appear to be installed in its default\n' \
      'location of:\n', args.package_maker, '\n'
    fail = True

  # Is what we are trying to distribute available?
  if args.packages_dir:
    if not os.path.exists(args.packages_dir):
      print '* Error: path provided:', args.packages_dir, 'not found'
      fail = True
  else:
    print '* Error: you need to supply a --packages-dir argument pointing\n' \
      'to where you installed everything to (--packages-dir /opt/moose)\n'
    fail = True

  # Has this already been attempted?
  if os.path.exists(args.base_path) and not args.force:
    print '* Warning: detecting previous build attempt at\n\n\t', args.base_path, \
      '\n\nDelete this location, or use --force\n'
    fail = True

  if fail:
    print '\nPlease solve for the failures identified and re-run this script'
    sys.exit(1)
  return args

def parseArguments(args=None):
  parser = argparse.ArgumentParser(description='Create Redistributable Package')
  parser.add_argument('-p', '--packages-dir', help='Directory where you installed everything to (/opt/moose)')
  parser.add_argument('--package-type', help='Specify type of package to build. Valid values: deb rpm pkg')
  parser.add_argument('-f', '--force', action='store_const', const=True, default=False, help='Overwrites previous redistributable package build attempt')
  return verifyArgs(parser.parse_args(args))

if __name__ == '__main__':
  args = parseArguments()

  # Set some useful variables about our current machine
  args.major, args.minor, args.patch = platform.mac_ver()[0].split('.')

  # Increment our redistributable version
  version_file_path = os.path.join(args.relative_path, 'OSX', '.'.join([args.major, args.minor]) + '_build')
  if os.path.exists(version_file_path):
    version_file = open(version_file_path, 'r')
    args.redistributable_version = int(version_file.read()) + 1
    version_file.close()
    version_file = open(version_file_path, 'w')
    version_file.write(str(args.redistributable_version))
    version_file.close()
    args.redistributable_name = _version_to_name['.'.join([args.major, args.minor])] + '-environment_' + str(args.redistributable_version) + '.pkg'
  else:
    print 'Can not find my version file in the usual place:', version_file_path
    sys.exit(1)

  print 'Preparing build area...'
  if prepare_area(args):
    tarball_file = create_tarball(args)
    if tarball_file:
      redistributable_file = create_redistributable(args)
      if redistributable_file:
        print 'Redistributable built! You should now sign the package using the following command:\n\n\t' \
          'productsign --sign "Developer ID Installer: BATTELLE ENERGY ALLIANCE, LLC (J2Y4H5G88N)"', \
          os.path.join(args.base_path, str(args.major) + str(args.minor) + '.pkg'), \
          os.path.join(args.base_path, args.redistributable_name), \
          '\n\nOnce complete, you can verify your package has been correctly signed by running the following command:\n\n\t', \
          'spctl -a -v --type install', os.path.join(args.base_path, args.redistributable_name)
