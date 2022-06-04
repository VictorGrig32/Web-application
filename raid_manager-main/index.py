from flask import Flask, request, render_template
from utilies.raid_manager import RaidManager
import time

raid = RaidManager()
raid.set_pass()

app = Flask(__name__)

menu = {'create' : 'Создать', 'control' : 'Управление', 'status' : 'Состояние'}

@app.route('/')
def index():
    text = [ 'WEB-интерфейс для управления RAID-массивами',
             'Разработал и реализовал студент 4-го курса',
             'Григоренко Виктор Русланович' ]
    
    return render_template('index.html', menu = menu, text=text)


@app.route('/create', methods=['POST', 'GET'])
def create():
    raid_types = { 'raid0' : 'RAID 0', 'raid1' : 'RAID 1', 
    'raid4' : 'RAID 4', 'raid5' : 'RAID 5',
    'raid6' : 'RAID 6', 'raid10' : 'RAID 10' }
    
    filesystems = { 'ext2' : 'ext2', 'ext3' : 'ext3', 'ext4' : 'ext4' }
    disks = raid.get_disks()

    if request.method == 'POST':
        selected_disks = request.form.getlist('disks')
        selected_raid_type = request.form.get('raid_type')
        selected_filesystem = request.form.get('filesystem')
        raid_name = '/dev/md' + request.form.get('raid_name')

        res = []

        for disk in selected_disks:
            res.append(f'Размонтирование диска {disk} и установка специальной файловой системы:')
            res.append(raid.umount_disk(disk))
            raid.change_disk_system_type(disk)
            res.append(f'Файловая система {disk} успешно изменена')

        res.append('Создание рейда:')
        res.append('RAID-массив успешно создан') if raid.create_raid(raid_name, selected_raid_type, selected_disks) else res.append('Ошибка при создании RAID-массива')

        res.append('Установка файловой системы на RAID-массив:')
        res.append(raid.create_raid_filesystem(raid_name, selected_filesystem))
        time.sleep(30)

        res.append('Создание точки монтирования для RAID-массива и монтирование его:')
        res.append(raid.mount_raid(raid_name))

        res.append('Создание конфигурационного файла и запись в него необходимых данных:')
        res.append('Файл успешно обновлён') if raid.create_conf_file() else res.append('Ошибка при обновлении файла')
        
        return render_template('create.html', menu = menu, raid_types = raid_types, disks = disks, filesystems = filesystems, text=res)
    
    text = [ 'Создание RAID-массива может занять некоторое время.',
             'Пожалуйста, не перезагружайте страницу для предотвращения критической ошибки во время создания RAID-массива' ]
    
    return render_template('create.html', menu = menu, raid_types = raid_types, disks = disks, filesystems = filesystems, text=text)

@app.route('/status', methods=['POST', 'GET'])
def status():
    status = raid.check_raid_stat()
    
    return render_template('status.html', menu = menu, status=status)

@app.route('/control', methods=['POST', 'GET'])
def control():

    if request.method == 'POST':
        raid_name = '/dev/md' + request.form.get('raid_name')
        
        raid.umount_raid(raid_name)
        raid.remove_raid(raid_name)
        
        return render_template('control.html', menu = menu)

    return render_template('control.html', menu = menu)

if __name__ == "__main__":
    app.run(debug=True)
