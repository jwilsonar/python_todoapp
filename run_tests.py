#!/usr/bin/env python
"""
Script para ejecutar tests de la aplicación TodoApp de manera organizada.
Proporciona comandos para diferentes tipos de tests y reportes de cobertura.
"""
import os
import sys
import subprocess


def run_command(command):
    """Ejecutar comando en el shell."""
    print(f"\n🚀 Ejecutando: {command}")
    print("=" * 60)
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ Comando ejecutado exitosamente")
    else:
        print(f"\n❌ Comando falló con código de salida: {result.returncode}")
    
    return result.returncode


def main():
    """Función principal del script."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # Comandos disponibles
    commands = {
        'all': run_all_tests,
        'models': run_model_tests,
        'forms': run_form_tests,
        'views': run_view_tests,
        'auth': run_auth_tests,
        'api': run_api_tests,
        'permissions': run_permission_tests,
        'coverage': run_coverage_tests,
        'quick': run_quick_tests,
        'setup': setup_test_environment,
        'clean': clean_test_data,
        'help': print_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Comando no reconocido: {command}")
        print_help()


def print_help():
    """Mostrar ayuda de comandos disponibles."""
    print("""
🧪 TodoApp Test Runner - Comandos Disponibles:

EJECUTAR TESTS:
  all         - Ejecutar todos los tests
  models      - Ejecutar solo tests de modelos
  forms       - Ejecutar solo tests de formularios
  views       - Ejecutar solo tests de vistas
  auth        - Ejecutar solo tests de autenticación
  api         - Ejecutar solo tests de APIs
  permissions - Ejecutar solo tests de permisos
  quick       - Ejecutar tests rápidos (sin base de datos)

ANÁLISIS:
  coverage    - Ejecutar tests con reporte de cobertura

UTILIDADES:
  setup       - Configurar entorno de tests
  clean       - Limpiar datos de test
  help        - Mostrar esta ayuda

EJEMPLOS:
  python run_tests.py all
  python run_tests.py models
  python run_tests.py coverage
    """)


def run_all_tests():
    """Ejecutar todos los tests."""
    print("🔍 Ejecutando todos los tests...")
    return run_command("python manage.py test tasks.tests --verbosity=2")


def run_model_tests():
    """Ejecutar tests de modelos."""
    print("📊 Ejecutando tests de modelos...")
    return run_command("python manage.py test tasks.tests.test_models --verbosity=2")


def run_form_tests():
    """Ejecutar tests de formularios."""
    print("📝 Ejecutando tests de formularios...")
    return run_command("python manage.py test tasks.tests.test_forms --verbosity=2")


def run_view_tests():
    """Ejecutar tests de vistas."""
    print("🌐 Ejecutando tests de vistas...")
    return run_command("python manage.py test tasks.tests.test_views --verbosity=2")


def run_auth_tests():
    """Ejecutar tests de autenticación."""
    print("🔐 Ejecutando tests de autenticación...")
    return run_command("python manage.py test tasks.tests.test_auth --verbosity=2")


def run_api_tests():
    """Ejecutar tests de APIs."""
    print("🚀 Ejecutando tests de APIs...")
    return run_command("python manage.py test tasks.tests.test_api --verbosity=2")


def run_permission_tests():
    """Ejecutar tests de permisos."""
    print("🛡️ Ejecutando tests de permisos...")
    return run_command("python manage.py test tasks.tests.test_permissions --verbosity=2")


def run_coverage_tests():
    """Ejecutar tests con reporte de cobertura."""
    print("📈 Ejecutando tests con cobertura...")
    
    # Verificar si coverage está instalado
    try:
        import coverage
    except ImportError:
        print("❌ Coverage no está instalado. Instalándolo...")
        run_command("pip install coverage")
    
    # Ejecutar tests con coverage
    commands = [
        "coverage erase",  # Limpiar datos previos
        "coverage run --source='.' manage.py test tasks.tests --verbosity=2",
        "coverage report --skip-covered",  # Reporte en consola
        "coverage html",  # Reporte HTML
    ]
    
    for cmd in commands:
        if run_command(cmd) != 0:
            print(f"❌ Error ejecutando: {cmd}")
            return
    
    print("\n📊 Reporte de cobertura generado en: htmlcov/index.html")


def run_quick_tests():
    """Ejecutar tests rápidos que no requieren base de datos."""
    print("⚡ Ejecutando tests rápidos...")
    # Tests que usan SimpleTestCase en lugar de TestCase
    return run_command("python manage.py test tasks.tests.test_forms --verbosity=2")


def setup_test_environment():
    """Configurar entorno de tests."""
    print("⚙️ Configurando entorno de tests...")
    
    commands = [
        "python manage.py collectstatic --noinput",
        "python manage.py migrate --run-syncdb",
    ]
    
    for cmd in commands:
        if run_command(cmd) != 0:
            print(f"❌ Error en configuración: {cmd}")
            return
    
    print("\n✅ Entorno de tests configurado correctamente")


def clean_test_data():
    """Limpiar datos de test."""
    print("🧹 Limpiando datos de test...")
    
    commands = [
        "python manage.py flush --noinput",  # Limpiar base de datos
        "rm -rf htmlcov/",  # Eliminar reportes de cobertura
        "rm -f .coverage",  # Eliminar archivo de cobertura
    ]
    
    for cmd in commands:
        run_command(cmd)
    
    print("\n✅ Datos de test limpiados")


if __name__ == "__main__":
    main() 