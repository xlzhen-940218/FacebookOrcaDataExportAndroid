# This is a sample Python script.
import os
import tarfile
import time

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

android_device = ''
package_name = 'com.facebook.orca'
apks_path = 'orca_apks'
app_data = 'orca_data'


# read android device please open usb debug
def read_android_device():
    result = os.popen('adb devices').read()
    if result.__contains__('\tdevice'):
        results = result.split('\n')
        global android_device
        android_device = results[1].split('\t')[0]
        print('connected android device : {0}'.format(android_device))
        return True
    else:
        print('device not found! please usb connect device and open usb debug')
        return False


# backup official apk ,program exited before re-install
def backup_official_apk():
    result = os.popen('adb -s {0} shell "pm path {1}"'.format(android_device, package_name)).read()
    results = result.split('\n')
    for line in results:
        if line.__contains__('package:'):
            path = line.split('package:')[1]
            if not os.path.exists(apks_path):
                os.mkdir(apks_path)
            print('copy split apk...')
            os.system('adb -s {0} pull {1} {2}/'.format(android_device, path, apks_path))
    return os.listdir(apks_path).__len__() > 0


# uninstall official apk wait install old version
def uninstall_app_with_out_data():
    result = os.popen('adb -s {0} shell pm uninstall -k {1}'.format(android_device, package_name)).read()
    return result.__contains__("Success")


# install old version app if failed need reboot system and retry
def install_old_version_app():
    result = os.popen('adb -s {0} install -r -d {1}'.format(android_device, '{0}.apk'.format(package_name))).read()
    return result.__contains__("Success")


# if install old version failed ,need reboot system
def reboot_system():
    os.system('adb -s {0} reboot'.format(android_device))
    time.sleep(15)  # sleep 15 seconds wait rebooting


# backup app data
def backup_app_data():
    os.system('adb -s {0} shell am start -n {1}/.auth.StartScreenActivity'.format(android_device, package_name))
    print('Please look your phone and click continue...')
    time.sleep(5)
    if not os.path.exists(app_data):
        os.mkdir(app_data)
    print('Please look your phone and input backup password 0000')
    os.system('adb -s {0} backup -f {1}/{2}.ab {2}'.format(android_device, app_data, package_name))
    return os.path.exists('{0}/{1}.ab'.format(app_data, package_name))


# backed data after re-install official apks
def install_official_apks():
    files = os.listdir(apks_path)
    apks = ''
    for file in files:
        apks = '{0} {1}/{2}'.format(apks, apks_path, file)
    os.system('adb -s {0} install-multiple  -r -d --user 0 {1}'.format(android_device, apks))


# unpack ab data
def unpack_ab_data():
    os.system('java -jar abp.jar unpack {0}/{1}.ab {0}/{1}.tar 0000 '.format(app_data, package_name))
    if os.path.exists('{0}/{1}.tar'.format(app_data, package_name)):
        os.system('7z.exe x "{0}/{1}.tar" -o"{0}/{1}" -r -y'.format(app_data, package_name))
        return True
    else:
        return False


if __name__ == '__main__':

    connected = read_android_device()
    if connected:
        backed_apks = backup_official_apk()
        if backed_apks:
            uninstalled = uninstall_app_with_out_data()
            if uninstalled:
                install_old_version = install_old_version_app()
                while not install_old_version:
                    reboot_system()
                    install_old_version = install_old_version_app()
                backed_data = backup_app_data()
                install_official_apks()
                if backed_data:
                    unpacked = unpack_ab_data()
                    if unpacked:
                        print('unpack success!')
                        db_path = os.path.abspath('{0}/{1}/apps/{1}/db'.format(app_data, package_name))
                        os.system('explorer.exe /e,/select, "{0}"'.format(db_path))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
