sudo docker network create --driver bridge netX \
--subnet=172.20.0.0/16
##################################
mkdir -p /home/diapps/scripts/jic_web
cd /home/diapps/scripts/jic_web
########################
cat > docker-compose.yml << "EOF"
version: "3.4"

services:
  jic_minio_storage:
    restart: "no"
    image: bitnamilegacy/minio:latest
    ports:
      - 9010:9000
      - 9011:9001
    environment:
      - MINIO_ROOT_USER=mast_st_jic
      - MINIO_ROOT_PASSWORD=KtWzuaY3Uy8F
      # - MINIO_ACCESS_KEY=mast_st_jic
      # - MINIO_SECRET_KEY=KtWzuaY3Uy8F
      - MINIO_CONSOLE_ADDRESS=:9001
      - TZ=UTC
    networks:
      netX:
        ipv4_address: 172.20.0.75
    volumes:
      - 'jicst_storage_data:/bitnami/minio/data'

  jicweb-master:
    image: 'bitnamilegacy/postgresql:17'
    ports:
      - '5440:5432'
    networks:
      netX:
        ipv4_address: 172.20.1.85
    volumes:
      - 'jicweb_master_data_v1:/bitnami/postgresql'
    environment:
      - POSTGRESQL_REPLICATION_MODE=master
      - POSTGRESQL_POSTGRES_PASSWORD=1*o63U9JlN5bLp
      - POSTGRESQL_REPLICATION_USER=repl_jicweb
      - POSTGRESQL_REPLICATION_PASSWORD=2U552^2UP?yU]>
      - POSTGRESQL_USERNAME=mast_jicweb
      - POSTGRESQL_PASSWORD=g0hNw,0p1M\v£Y
      - POSTGRESQL_DATABASE=db_jicweb

  jicweb-slave:
    image: 'bitnamilegacy/postgresql:17'
    ports:
      - '5432'
    networks:
      - netX
    depends_on:
      - jicweb-master
    environment:
      - POSTGRESQL_REPLICATION_MODE=slave
      - POSTGRESQL_REPLICATION_USER=repl_jicweb
      - POSTGRESQL_REPLICATION_PASSWORD=2U552^2UP?yU]>
      - POSTGRESQL_MASTER_HOST=172.20.1.85
      - POSTGRESQL_PASSWORD=g0hNw,0p1M\v£Y
      - POSTGRESQL_MASTER_PORT_NUMBER=5432

volumes:
  jicst_storage_data:
    driver: local
  jicweb_master_data_v1:
    driver: local

networks:
  netX:
    name: netX
    external: true
EOF
#########################
docker-compose up -d
#########################
WSL_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "========================================"
echo "Contenedores levantados."
echo "WSL IP: $WSL_IP"
echo ""
echo "Para acceder a MinIO desde Windows,"
echo "corre esto en PowerShell (Administrador):"
echo ""
echo "  netsh interface portproxy add v4tov4 listenport=9010 listenaddress=0.0.0.0 connectport=9010 connectaddress=$WSL_IP"
echo "  netsh interface portproxy add v4tov4 listenport=9011 listenaddress=0.0.0.0 connectport=9011 connectaddress=$WSL_IP"
echo ""
echo "Luego accede en: http://localhost:9011"
echo "========================================"