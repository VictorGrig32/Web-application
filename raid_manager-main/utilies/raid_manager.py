import os
import subprocess
from getpass import getpass

class RaidManager:
    '''
    Класс для управления RAID-массивом
    '''

    # Поле, хранящее пароль для работы с инструкциями
    __sudo_pass = ''
    
    def set_pass(self):
        '''
        Метод, который позволяет получить пароль от пользователя для работы с sudo-коммандами
        '''

        self.sudo_pass = getpass('Sudo password:')

    def get_pass(self):
        '''
        Метод, который возвращает пароль, введённый пользователем
        '''

        return self.sudo_pass

    def get_disks(self):
        '''
        Метод, который возвращает информацию о дисковых устройствах компьютера
        '''

        try:
            tmp = os.popen('lsblk | egrep "sd"').read().split('\n')
            tmp2 = []
            res = dict()

            for row in tmp:
                if row.find('sda') == -1:
                    for word in row.split(' '):
                        if word != '':
                            tmp2.append(word)

            tmp.clear()
            
            for row in tmp2:
                if row.find('sd') != -1:
                    tmp.append('/dev/' + row)
                elif row.find('G') != -1:
                    tmp.append(row)

            count = int((len(tmp) / 2))
            
            for i in range(count):
                res[tmp[i*2]] = tmp[i*2] + ' ' + tmp[(i*2)+1]
            
        except Exception:
            return Exception
        else:
            return res

    def umount_disk(self, disk):
        '''
        Метод, который позволяет размонтировать выбранные диски для RAID-массива
        '''

        try:
            res = subprocess.getstatusoutput(f'umount {disk}')[1]
        except Exception:
            return Exception
        else:
            return res

    def change_disk_system_type(self, disk):
        '''
        Метод, который позволяет изменить тип разделов, которые будут входить в будущий RAID-массив
        '''

        try:
            path = os.path.dirname(os.path.abspath(__file__))
            proc = subprocess.Popen([f'{path}/fdisk_helper.sh', f'{disk}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc.wait()
            res = proc.stdout.read()
        except Exception:
            return Exception
        else:
            return res

    def create_raid(self, name, level, disks):
        '''
        Метод, который позволяет создать RAID-массив с заданным уровнем и выбранными
        пользователем разделами
        '''

        size = len(disks)
        command = ['mdadm', '--create', '--verbose', f'{name}', f'--level={level}', f'--raid-devices={size}']
        
        for i in range(size):
            command.append(f'{disks[i]}')

        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            proc = os.popen(' '.join(command), 'w').write('y')
            os.popen('exit')
        except Exception:
            return False
        else:
            return True

    def create_raid_filesystem(self, raid_name, filesystem):
        '''
        Метод, позволяющий создать выбранную файловую систему на созданном RAID-массиве
        '''
        
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            proc = subprocess.Popen([f'{path}/mkfs_helper.sh', f'mkfs.{filesystem}', f'{disk}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc.wait()
            res = proc.stdout.read()
        except Exception:
            return Exception
        else:
            return f'Файловая система {raid_name} успешно изменена на {filesystem}'

    def mount_raid(self, raid_name):
        '''
        Метод, позволяющий примонтировать созданный RAID-массив
        '''
        
        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            os.popen(f'mkdir /raid')
            res = os.popen(f'mount {raid_name} /raid').read()
            os.popen('exit')
        except Exception:
            return Exception
        else:
            return f'RAID-массив {raid_name} успешно смонтирован в /raid'

    def check_raid_stat(self):
        '''
        Метод, позволяющий узнать статус RAID-массивов
        '''

        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            res = os.popen(f'cat /proc/mdstat').read().split('\n')
            os.popen('exit')
        except Exception:
            return Exception
        else:
            return res

    def remove_raid(self, raid_name):
        '''
        Метод, позволяющий размонтировать RAID-массив
        '''

        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            res = os.popen(f'mdadm -S {raid_name}').read().split('\n')
            os.popen('exit')
        except Exception:
            return Exception
        else:
            return res

    def umount_raid(self, raid_name):
        '''
        Метод, позволяющий остановить RAID-массив
        '''

        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            res = os.popen(f'umount {raid_name}').read().split('\n')
            os.popen('exit')
        except Exception:
            return Exception
        else:
            return res

    def create_conf_file(self):
        '''
        Метод, создающий и записывающий информацию о RAID-массиве в конфигурационный файл
        для правильного определения RAID-массива при запуске системы
        '''

        try:
            os.popen('sudo su', 'w').write(self.sudo_pass)
            os.popen('echo "DEVICE partitions" > /etc/mdadm/mdadm.conf')
            os.popen("mdadm --detail --scan --verbose | awk '/ARRAY {print}' >> /etc/mdadm/mdadm.conf")
            os.popen('exit')
        except Exception:
            return Exception
        else:
            return True
