# White Label Login V5.1 Empresarial

Versión 5.1 del portal empresarial. Esta revisión mejora la V5 y la deja más lista para uso real.

## Mejoras de la V5.1
- **migración inicial incluida**
- **script de arranque Windows mejorado**
- **configuración Docker ajustada**
- **ruta de API de permisos y usuarios**
- **seed inicial más consistente**
- **tests base incluidos**
- **fallback a SQLite local para pruebas rápidas**
- **documentación más clara para GitHub y despliegue**

## Funcionalidades
- Login, logout y registro
- Recuperación de contraseña
- 2FA por correo
- 2FA por app autenticadora
- Roles: `superadmin`, `admin`, `manager`, `user`
- Permisos granulares
- Multiempresa / multisucursal
- Dashboard administrativo
- Auditoría
- API REST con Bearer Token
- Exportación CSV
- Docker + PostgreSQL + Gunicorn + Nginx

## Usuario inicial
- Correo: `superadmin@local.test`
- Contraseña: `ChangeMe123!`

## Inicio rápido Windows
```bat
scripts\setup_windows.bat
```

Luego:
```bat
.venv\Scripts\activate
python run.py
```

Abrir:
- http://127.0.0.1:8000

## Inicio rápido Docker
```bash
copy .env.example .env
docker compose up --build -d
docker compose exec web python seed_data.py
```

## API
### Health
```bash
curl http://127.0.0.1:8000/api/health
```

### Stats
```bash
curl -H "Authorization: Bearer TU_API_TOKEN" http://127.0.0.1:8000/api/stats
```

### Users
```bash
curl -H "Authorization: Bearer TU_API_TOKEN" http://127.0.0.1:8000/api/users
```

### Permissions matrix
```bash
curl -H "Authorization: Bearer TU_API_TOKEN" http://127.0.0.1:8000/api/permissions
```

## Tests
```bash
pytest -q
```

## GitHub desde Windows
```bash
cd C:\RUTA\whitelabel_login_v5_1
git init
git branch -M main
git add .
git commit -m "feat: white label login v5.1 empresarial"
git remote add origin https://github.com/TU_USUARIO/whitelabel_login_v5_1.git
git push -u origin main
```
