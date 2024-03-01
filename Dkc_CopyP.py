import os
import subprocess
from ftplib import FTP

try:
    # Definir Variables de Contenedor->Servidor
    docker_ps_output = subprocess.check_output(["sudo", "docker", "ps"]).decode()
    container_name_or_id = [line.split()[0] for line in docker_ps_output.split('\n') if 'build' in line][0]
    container_dir = "/usr/src/app/entity/bankdebits"
    host_dir = "/home/root_wso/RespaldoEnviados"

    # Definir Variables de Servidor->FTP
    ftp_user = "Debbancario"
    ftp_password = "Xtr3m#2023"
    ftp_host = "140.27.120.102"

    # Directorios locales de origen
    dirs_origen = [
        "/home/root_wso/RespaldoEnviados/bankdebits/sci",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancobolivariano",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancopacifico",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancoguayaquil",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancoprodubanco",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancopichincha",
        "/home/root_wso/RespaldoEnviados/bankdebits/bancointernacional"
    ]

    # Directorios remotos de destino
    dirs_host_r = [
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/sci",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancobolivariano",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancopacifico",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancoguayaquil",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancoprodubanco",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancopichincha",
        "/DebitosBancarios/PRODUCCION/ARCHIVOS_ENVIADOS_TYTAN/bankdebits/bancointernacional"
    ]

    # Parte Docker_Copy
    docker_ps_output = subprocess.check_output(["sudo", "docker", "ps"]).decode()
    print(docker_ps_output)

    # Verificar si se encontró un contenedor
    if not container_name_or_id:
        print("No se encontró ningún contenedor con 'build' en su nombre o ID.")
        exit(1)

    # Verificar si la ruta HOST_DIR existe, si no existe, crearla
    if not os.path.isdir(host_dir):
        print("El Script detectó que la ruta de destino no existe, por lo tanto procederá a crearse.")
        os.makedirs(host_dir)

    # Verificar si la ruta CONTAINER_DIR en el contenedor existe
    container_dir_check = f"sudo docker exec {container_name_or_id} [ -d {container_dir} ]"
    if subprocess.call(container_dir_check, shell=True) != 0:
        print("La ruta del contenedor no existe. Revisar la Ruta de Origen, finalizando proceso.")
        exit(1)
    else:
        print("La ruta del contenedor sí existe, procediendo con el copiado.")

    # Copiar archivos desde el contenedor al host
    docker_cp_command = f"sudo docker cp {container_name_or_id}:{container_dir} {host_dir}"
    print(docker_cp_command)
    subprocess.run(docker_cp_command, shell=True)

    # Cambiar permisos de los archivos copiados
    os.chmod(host_dir, 0o777)
    print(f"Archivos copiados desde el contenedor a {host_dir}")

    # Parte FTP
    # Establecer conexión FTP
    try:
        with FTP(ftp_host) as ftp:
            ftp.login(user=ftp_user, passwd=ftp_password)
            print("Conexión exitosa a NAS.")
            for dir_origen, dir_host_r in zip(dirs_origen, dirs_host_r):
                ftp.cwd(dir_host_r)
                os.chdir(dir_origen)
                for filename in os.listdir():
                    with open(filename, 'rb') as file:
                        ftp.storbinary(f'STOR {filename}', file)
            print("Transferencia de archivos exitosa.")
    except Exception as e:
        print(f"Fallo la conexión a NAS. Error: {e}")
        exit(1)

    # Preguntar al usuario si desea eliminar archivos locales
    opcion = input("¿Deseas eliminar los archivos locales de las carpetas de bankdebits? (Y/N): ")
    if opcion.lower() == "y":
        for dir_origen in dirs_origen:
            for file in os.listdir(dir_origen):
                os.remove(os.path.join(dir_origen, file))
        print("Archivos locales eliminados.")
    else:
        print("No se han eliminado archivos locales.")
except Exception as e:
    print("Dkc_CopyP.py - Error Global: ", e)

