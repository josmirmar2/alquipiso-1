import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Alojamiento, Cliente, Propietario, Reserva
from django.contrib.messages import get_messages
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.test import LiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone


class LoginTestCase(TestCase):
    def setUp(self):
        # Crear un usuario para pruebas
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        # Probar un login exitoso
        response = self.client.post(reverse('alquileres:login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # Redirige después del login
        self.assertRedirects(response, reverse('alquileres:index'))  # O la URL de destino esperada
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        # Probar un login fallido
        response = self.client.post(reverse('alquileres:login'), {
            'username': self.username,
            'password': "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)  # La página se recarga
        self.assertContains(response, "Credenciales inválidas")


class RegisterViewTestCase(TestCase):
    
    def setUp(self):
        # Inicializa un usuario base para pruebas
        self.email = "testuser@example.com"
        self.password = "testpassword123"
        self.nombre = "Test"
        self.apellido = "User"
        self.telefono = "123456789"
    
    def test_register_success_cliente(self):
        # Prueba de registro exitoso para un Cliente
        response = self.client.post(reverse('alquileres:register'), {
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'password': self.password,
            'confirm_password': self.password,
            'role': 'cliente',
        })

        # Verifica que el código de respuesta sea una redirección (registro exitoso)
        self.assertEqual(response.status_code, 302)
        
        # Verifica que el usuario ha sido creado
        user = User.objects.get(email=self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.first_name, self.nombre)
        self.assertEqual(user.last_name, self.apellido)

        # Verifica que el cliente ha sido creado
        cliente = Cliente.objects.get(user=user)
        self.assertEqual(cliente.telefono, self.telefono)
        
        # Verifica que el usuario está autenticado
        self.assertTrue(self.client.login(username=self.email, password=self.password))

    def test_register_success_propietario(self):
        # Prueba de registro exitoso para un Propietario
        response = self.client.post(reverse('alquileres:register'), {
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'password': self.password,
            'confirm_password': self.password,
            'role': 'propietario',
        })

        # Verifica que el código de respuesta sea una redirección (registro exitoso)
        self.assertEqual(response.status_code, 302)
        
        # Verifica que el usuario ha sido creado
        user = User.objects.get(email=self.email)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.first_name, self.nombre)
        self.assertEqual(user.last_name, self.apellido)

        # Verifica que el propietario ha sido creado
        propietario = Propietario.objects.get(user=user)
        self.assertEqual(propietario.telefono, self.telefono)
        
        # Verifica que el usuario está autenticado
        self.assertTrue(self.client.login(username=self.email, password=self.password))

    def test_register_email_exists(self):
        # Crea un usuario previamente
        User.objects.create_user(username="existinguser@example.com", email="existinguser@example.com", password="password123")
        
        # Intenta registrar otro usuario con el mismo correo
        response = self.client.post(reverse('alquileres:register'), {
            'email': 'existinguser@example.com',
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'password': self.password,
            'confirm_password': self.password,
            'role': 'cliente',
        })

        # Verifica que te redirige a la pagina de login
        self.assertEqual(response.status_code, 302)
        
        # Verifica que se muestra el mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'El correo electrónico ya está registrado.')

    def test_register_password_mismatch(self):
        # Intenta registrar un usuario con contraseñas que no coinciden
        response = self.client.post(reverse('alquileres:register'), {
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'password': self.password,
            'confirm_password': 'wrongpassword',  # Contraseña no coincide
            'role': 'cliente',
        })

        # Verifica que el formulario no se haya enviado (no redirige)
        self.assertEqual(response.status_code, 200)
        
        # Verifica que se muestra el mensaje de error de contraseñas no coincidentes
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Las contraseñas no coinciden.')
        
        
class EditUserProfileTestCase(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username="testuser@example.com", password="testpassword123", first_name="Nombre", last_name="Apellido")
        self.cliente = Cliente.objects.create(user=self.user)
        self.client.login(username="testuser@example.com", password="testpassword123")
        
        self.url = reverse('alquileres:user_profile')  # URL de la vista de perfil del usuario
    
    def test_editar_perfil_valido(self):
    # Asegúrate de que el usuario está autenticado
        self.client.login(username='testuser', password='password123')

    # Datos del formulario con una contraseña nueva válida
        data = {
            'email': "newemail@example.com",
            'first_name': "Nuevo Nombre",
            'last_name': "Nuevo Apellido",
            'current_password': "",  
            'new_password': "",
            'confirm_new_password': ""  
        }

        response = self.client.post(self.url, data)

        # Verificar que los datos del usuario se han actualizado correctamente
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        self.assertEqual(self.user.first_name, "Nuevo Nombre")
        self.assertEqual(self.user.last_name, "Nuevo Apellido")

        # Verificar que el código de estado es 200 (sin redirección)
        self.assertEqual(response.status_code, 200)

        # Verificar que la respuesta contiene el formulario con los datos actualizados
        self.assertContains(response, 'Nuevo Nombre')
        self.assertContains(response, 'Nuevo Apellido')
        self.assertContains(response, 'newemail@example.com')

    def test_editar_perfil_invalido(self):
        # Datos del formulario inválidos
        data = {
            'email': 'newemail@example.com',
            'first_name': 'Nuevo Nombre',
            'last_name': 'Nuevo Apellido',
            'current_password': 'wrongpassword',  # Contraseña incorrecta
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        
        response = self.client.post(reverse('alquileres:user_profile'), data)

        # Verificar que no se actualizó la información
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, 'newemail@example.com')
        self.assertNotEqual(self.user.first_name, 'Nuevo Nombre')
        self.assertNotEqual(self.user.last_name, 'Nuevo Apellido')
        
        # Asegurarse de que el formulario no se haya procesado
        self.assertEqual(response.status_code, 200)




        
class CreateAlojamientoTestCase(TestCase):
    
    def setUp(self):
        # Crear un usuario y asociarle un propietario
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.propietario = Propietario.objects.create(user=self.user, telefono='123456789')
        self.client.login(username='testuser', password='testpassword')

        # Crear datos para un alojamiento
        self.alojamiento_data = {
            'nombre': 'Alojamiento Test',
            'direccion': 'Calle Test 123',
            'ciudad': 'Test City',
            'descripcion': 'Descripción del alojamiento de prueba.',
            'precio': 100.0,
            'imagen': 'null',
        }

    def test_create_alojamiento_no_propietario(self):
        # Probar que un usuario sin propietario no puede crear un alojamiento
        # Desasociar al propietario
        self.user.propietario.delete()
        
        response = self.client.post(reverse('alquileres:create_alojamiento'), self.alojamiento_data)
        
        # Verificar que se redirige a la página de inicio (o la página de tu preferencia)
        self.assertRedirects(response, reverse('index'))

    def test_create_alojamiento_success(self):
        # Probar que un propietario autenticado puede crear un alojamiento
        response = self.client.post(reverse('alquileres:create_alojamiento'), self.alojamiento_data)
        
        # Verificar que el alojamiento se ha guardado
        self.assertEqual(Alojamiento.objects.count(), 1)
        
        alojamiento = Alojamiento.objects.first()
        self.assertEqual(alojamiento.nombre, 'Alojamiento Test')
        self.assertEqual(alojamiento.propietario, self.propietario)

        # Verificar que se redirige a la lista de alojamientos del propietario
        self.assertRedirects(response, reverse('alquileres:list_alojamientos_propietario', args=[self.propietario.id]))

    def test_create_alojamiento_invalid_form(self):
        # Probar que el formulario no se envía si falta algún campo obligatorio
        invalid_data = self.alojamiento_data.copy()
        del invalid_data['nombre']  # Eliminar un campo obligatorio
        
        response = self.client.post(reverse('alquileres:create_alojamiento'), invalid_data)
        
        # Verificar que el formulario no se haya enviado correctamente (status code 200)
        self.assertEqual(response.status_code, 200)
        
class EditAlojamientoTestCase(TestCase):
    def setUp(self):
        # Crear un propietario y un alojamiento de prueba
        self.user = User.objects.create_user(username="propietario", password="password123")
        self.propietario = Propietario.objects.create(user=self.user, telefono="123456789")
        self.alojamiento = Alojamiento.objects.create(
            nombre="Alojamiento de Prueba",
            direccion="Calle Falsa 123",
            ciudad="Springfield",
            descripcion="Descripción inicial",
            precio=100.0,
            propietario=self.propietario,
            activo=True
        )
        self.url = reverse('alquileres:edit_alojamiento', args=[self.alojamiento.id])

    def test_editar_alojamiento_valido(self):
        # Iniciar sesión como propietario
        self.client.login(username="propietario", password="password123")
        data = {
            'nombre': "Nuevo Nombre",
            'direccion': "Nueva Dirección",
            'ciudad': "Nueva Ciudad",
            'descripcion': "Nueva descripción",
            'precio': 150.0,
            'activo': False
        }
        response = self.client.post(self.url, data)
        self.alojamiento.refresh_from_db()

        # Comprobar que se actualizaron los datos
        self.assertEqual(self.alojamiento.nombre, "Nuevo Nombre")
        self.assertEqual(self.alojamiento.precio, 150.0)
        self.assertFalse(self.alojamiento.activo)

        # Comprobar redirección
        self.assertRedirects(response, reverse('alquileres:list_alojamientos_propietario', args=[self.propietario.id]))


    def test_formulario_invalido(self):
        # Iniciar sesión como propietario
        self.client.login(username="propietario", password="password123")
        response = self.client.post(self.url, {
            'nombre': "",  # Campo vacío
        })
        # Asegurarse de que no se realizó la actualización
        self.alojamiento.refresh_from_db()
        self.assertNotEqual(self.alojamiento.nombre, "")

        self.assertEqual(response.status_code, 200)


class CreateReservaTestCase(TestCase):

    def setUp(self):
        # Crear un usuario
        self.user = User.objects.create_user(username='testuser@example.com', password='testpassword')

        # Crear un Propietario para el usuario
        self.propietario = Propietario.objects.create(user=self.user, telefono="123456789")

        # Crear un cliente
        self.cliente = Cliente.objects.create(user=self.user, telefono="123456789")
        self.client.login(username='testuser@example.com', password='testpassword')

        # Crear un alojamiento
        self.alojamiento = Alojamiento.objects.create(
            nombre='Test Alojamiento',
            direccion='Test Direccion',
            ciudad='Test Ciudad',
            descripcion='Test Descripcion',
            precio=100.0,
            propietario=self.propietario,  # Asegúrate de que el alojamiento tenga un propietario
            activo=True
        )

        # URL para la vista de crear reserva
        self.url = reverse('alquileres:create_reserva', args=[self.alojamiento.id])

    def test_create_reserva_valid(self):
        data = {
            'fecha_entrada': timezone.now().date(),
            'fecha_salida': (timezone.now() + timezone.timedelta(days=2)).date(),
        }
        response = self.client.post(self.url, data)

        # Comprobar que la reserva se creó correctamente
        reserva = Reserva.objects.first()
        self.assertEqual(reserva.alojamiento, self.alojamiento)
        self.assertEqual(reserva.cliente, self.cliente)
        self.assertEqual(response.status_code, 302)  # Redirección a detalles de la reserva

    def test_create_reserva_alojamiento_inactivo(self):
        # Cambiar el estado del alojamiento a inactivo
        self.alojamiento.activo = False
        self.alojamiento.save()

        data = {
            'fecha_entrada': timezone.now().date(),
            'fecha_salida': (timezone.now() + timezone.timedelta(days=2)).date(),
        }
        response = self.client.post(self.url, data)

        # Comprobar que no se ha creado la reserva y se redirige con un mensaje de error
        self.assertEqual(response.status_code, 302)  # Redirección al índice

#--------------------------------------------------------- SELENIUM ----------------------------------------------------------------


class LoginTestCase(LiveServerTestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username="testuser@example.com", password="testpassword")
        
        # Usar ruta absoluta para chromedriver
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'drivers', 'chromedriver', 'chromedriver')
        print(f"ChromeDriver Path: {chromedriver_path}")  # Añadir esta línea para verificar la ruta en la consola

        service = Service(chromedriver_path)
        self.browser = webdriver.Chrome(service=service)

    def test_login_success(self):
        # Prueba de login
        self.browser.get(self.live_server_url + '/alquileres/login/')
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        username_field.send_keys('testuser@example.com')
        password_field.send_keys('testpassword')
        login_button.click()
        self.assertEqual(self.browser.current_url, self.live_server_url + '/alquileres/')

    def test_login_invalid_credentials(self):
        # Intentar hacer login con credenciales incorrectas
        self.browser.get(self.live_server_url + '/alquileres/login/')
        
        # Encontrar los campos del formulario
        username_field = self.browser.find_element(By.NAME, 'username')
        password_field = self.browser.find_element(By.NAME, 'password')
        login_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Ingresar credenciales incorrectas
        username_field.send_keys('wronguser@example.com')
        password_field.send_keys('wrongpassword')

        # Hacer clic en el botón de iniciar sesión
        login_button.click()

        # Verificar que se muestra un mensaje de error
        error_message = self.browser.find_element(By.CLASS_NAME, 'alert-danger')
        self.assertIn("Credenciales inválidas", error_message.text)

    def test_login_empty_fields(self):
        # Intentar hacer login con campos vacíos
        self.browser.get(self.live_server_url + '/alquileres/login/')
        
        # Encontrar el botón de login
        login_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Hacer clic en el botón de login sin llenar los campos
        login_button.click()

        # Verificar que la página sigue en el formulario de login
        self.assertEqual(self.browser.current_url, self.live_server_url + '/alquileres/login/')


    def tearDown(self):
        # Cerrar el navegador después de la prueba
        self.browser.quit()

class RegisterTestCase(LiveServerTestCase):
    def setUp(self):
        # Usar ruta absoluta para chromedriver
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'drivers', 'chromedriver', 'chromedriver')
        print(f"ChromeDriver Path: {chromedriver_path}")  # Añadir esta línea para verificar la ruta en la consola

        self.existing_user_email = 'testuser@example.com'
        self.existing_user_password = 'password123'
        self.existing_user = User.objects.create_user(
            username=self.existing_user_email,
            email=self.existing_user_email,
            password=self.existing_user_password
        )

        service = Service(chromedriver_path)
        self.browser = webdriver.Chrome(service=service)

    def test_register_valid(self):
        # Prueba de registro con datos válidos
        self.browser.get(self.live_server_url + '/alquileres/register/')
        
        # Encontrar los campos del formulario
        email_field = self.browser.find_element(By.NAME, 'email')
        nombre_field = self.browser.find_element(By.NAME, 'nombre')
        apellido_field = self.browser.find_element(By.NAME, 'apellido')
        telefono_field = self.browser.find_element(By.NAME, 'telefono')
        password_field = self.browser.find_element(By.NAME, 'password')
        confirm_password_field = self.browser.find_element(By.NAME, 'confirm_password')
        role_field = self.browser.find_element(By.NAME, 'role')
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Completar el formulario con datos válidos
        email_field.send_keys('newuser@example.com')
        nombre_field.send_keys('Test')
        apellido_field.send_keys('User')
        telefono_field.send_keys('123456789')
        password_field.send_keys('password123')
        confirm_password_field.send_keys('password123')
        role_field.send_keys('Cliente')  # Asumiendo que 'cliente' es la opción seleccionable
        
        # Desplazar la página hasta el final para hacer el botón visible
        self.browser.execute_script("arguments[0].scrollIntoView();", submit_button)  # Hacer scroll hasta el botón
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(submit_button))  # Esperar hasta que el botón sea clickeable
        
        self.browser.execute_script("arguments[0].click();", submit_button)  # Hacer clic en el botón

        # Verificar que se ha redirigido correctamente
        self.assertEqual(self.browser.current_url, self.live_server_url + '/')

    def test_register_empty_fields(self):
        # Intentar registrar con campos vacíos
        self.browser.get(self.live_server_url + '/alquileres/register/')
        
        # Encontrar el botón de enviar
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        # Desplazar la página hasta el final para hacer el botón visible
        self.browser.execute_script("arguments[0].scrollIntoView();", submit_button)
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(submit_button))  # Esperar hasta que el botón sea clickeable
        
        # Hacer clic en el botón sin llenar los campos
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Verificar que la página sigue en el formulario de registro
        self.assertEqual(self.browser.current_url, self.live_server_url + '/alquileres/register/')

    def test_register_email_exists(self):
        # Intentar registrar un correo que ya está en la base de datos
        self.browser.get(self.live_server_url + '/alquileres/register/')
        
        # Crear un usuario con el correo ya existente
        email_field = self.browser.find_element(By.NAME, 'email')
        nombre_field = self.browser.find_element(By.NAME, 'nombre')
        apellido_field = self.browser.find_element(By.NAME, 'apellido')
        telefono_field = self.browser.find_element(By.NAME, 'telefono')
        password_field = self.browser.find_element(By.NAME, 'password')
        confirm_password_field = self.browser.find_element(By.NAME, 'confirm_password')
        role_field = self.browser.find_element(By.NAME, 'role')
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Completar el formulario con el correo ya existente
        email_field.send_keys('testuser@example.com')  # Este correo ya existe en la base de datos
        nombre_field.send_keys('Test')
        apellido_field.send_keys('User')
        telefono_field.send_keys('123456789')
        password_field.send_keys('password123')
        confirm_password_field.send_keys('password123')
        role_field.send_keys('Cliente')  # Asumiendo que 'cliente' es la opción seleccionable
        
        # Desplazar la página hasta el final para hacer el botón visible
        self.browser.execute_script("arguments[0].scrollIntoView();", submit_button)
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(submit_button))  # Esperar hasta que el botón sea clickeable
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Verificar que el sistema redirige al login, ya que el correo ya está registrado
        self.assertEqual(self.browser.current_url, self.live_server_url + '/alquileres/login/')

    def tearDown(self):
        # Cerrar el navegador después de la prueba
        self.browser.quit()


class CreateReservaUITestCase(LiveServerTestCase):
    def setUp(self):
        # Configurar el servicio de ChromeDriver
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'drivers', 'chromedriver', 'chromedriver')
        service = Service(chromedriver_path)
        self.browser = webdriver.Chrome(service=service)

        # Crear usuario y cliente
        self.user1 = User.objects.create_user(username="propietario@example.com", password="password123")
        self.user2 = User.objects.create_user(username="cliente@example.com", password="password123")
        self.propietario = Propietario.objects.create(user=self.user1, telefono="123456789")
        self.cliente = Cliente.objects.create(user=self.user2, telefono="123456789")

        # Crear alojamiento
        self.alojamiento = Alojamiento.objects.create(
            nombre="Alojamiento Activo",
            direccion="Dirección",
            ciudad="Ciudad",
            descripcion="Descripción",
            precio=100.0,
            activo=True,
            propietario=self.propietario,
        )


    def test_reserva_valida(self):
        # Iniciar sesión
        self.browser.get(self.live_server_url + "/alquileres/login/")
        self.browser.find_element(By.NAME, "username").send_keys("cliente@example.com")
        self.browser.find_element(By.NAME, "password").send_keys("password123")
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Acceder a la página de reserva
        self.browser.get(self.live_server_url + f"/alquileres/create_reserva/{self.alojamiento.id}/")

        # Completar formulario
        self.browser.find_element(By.ID, "fecha_entrada").send_keys("01-12-2028")
        self.browser.find_element(By.ID, "fecha_salida").send_keys("05-12-2028")
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.browser.execute_script("arguments[0].scrollIntoView();", submit_button)
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Verificar redirección
        self.assertIn("/alquileres/detalles_reserva/", self.browser.current_url)

    def tearDown(self):
        self.browser.quit()


class EditAlojamientoUITestCase(LiveServerTestCase):
    def setUp(self):
        # Configurar WebDriver
        chromedriver_path = os.path.join(os.path.dirname(__file__), '..', '..', 'drivers', 'chromedriver', 'chromedriver')
        service = Service(chromedriver_path)
        self.browser = webdriver.Chrome(service=service)

        # Crear datos de prueba
        self.user = User.objects.create_user(username="propietario@example.com", password="password123")
        self.propietario = Propietario.objects.create(user=self.user, telefono="123456789")
        self.alojamiento = Alojamiento.objects.create(
            nombre="Alojamiento de Prueba",
            direccion="Calle Falsa 123",
            ciudad="Springfield",
            descripcion="Descripción inicial",
            precio=100.0,
            propietario=self.propietario,
            activo=True
        )

        self.edit_url = self.live_server_url + reverse('alquileres:edit_alojamiento', args=[self.alojamiento.id])

    def test_editar_alojamiento_valido(self):
        # Iniciar sesión
        self.browser.get(self.live_server_url + "/alquileres/login/")
        self.browser.find_element(By.NAME, "username").send_keys("propietario@example.com")
        self.browser.find_element(By.NAME, "password").send_keys("password123")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Acceder a la página de edición
        self.browser.get(self.edit_url)

        # Modificar el formulario
        self.browser.find_element(By.ID, "id_nombre").clear()
        self.browser.find_element(By.ID, "id_nombre").send_keys("Nuevo Nombre")
        self.browser.find_element(By.ID, "id_precio").clear()
        self.browser.find_element(By.ID, "id_precio").send_keys("200")
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.browser.execute_script("arguments[0].scrollIntoView();", submit_button)
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Verificar redirección
        self.assertIn(f"/propietario/{self.propietario.id}/alojamientos", self.browser.current_url)

    def tearDown(self):
        self.browser.quit()
        

class EditUserProfileUITest(LiveServerTestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username="testuser@example.com", password="testpassword123", email="testuser@example.com")
        self.url = reverse('alquileres:user_profile')

        # Usar Selenium para iniciar el navegador
        self.browser = webdriver.Chrome()

        # Loguear al usuario
        self.browser.get(self.live_server_url + '/alquileres/login/')
        self.browser.find_element(By.NAME, "username").send_keys("testuser@example.com")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def test_cargar_perfil(self):
        # Navegar a la página de editar perfil
        self.browser.get(self.live_server_url + self.url)

        # Verificar que los campos del formulario están presentes
        self.assertTrue(self.browser.find_element(By.NAME, "email"))
        self.assertTrue(self.browser.find_element(By.NAME, "first_name"))
        self.assertTrue(self.browser.find_element(By.NAME, "last_name"))
        self.assertTrue(self.browser.find_element(By.NAME, "current_password"))
        self.assertTrue(self.browser.find_element(By.NAME, "new_password"))
        self.assertTrue(self.browser.find_element(By.NAME, "confirm_new_password"))

        email_field = WebDriverWait(self.browser, 10).until(
        EC.visibility_of_element_located((By.NAME, "email"))
        )

        # Verificar que los datos actuales del usuario están cargados en el formulario
        self.assertEqual(email_field.get_attribute('value'), 'testuser@example.com')

    def test_editar_perfil_valido(self):
        # Navegar a la página de editar perfil
        self.browser.get(self.live_server_url + self.url)

        # Completar el formulario con nuevos datos
        self.browser.find_element(By.NAME, "email").clear()
        self.browser.find_element(By.NAME, "email").send_keys("newemail@example.com")
        self.browser.find_element(By.NAME, "first_name").clear()
        self.browser.find_element(By.NAME, "first_name").send_keys("Nuevo Nombre")
        self.browser.find_element(By.NAME, "last_name").clear()
        self.browser.find_element(By.NAME, "last_name").send_keys("Nuevo Apellido")

        # Enviar el formulario
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        # Esperar que la página se recargue y verificar que los datos se han actualizado
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.NAME, "first_name")))
        self.assertEqual(self.browser.find_element(By.NAME, "first_name").get_attribute('value'), 'Nuevo Nombre')
        self.assertEqual(self.browser.find_element(By.NAME, "last_name").get_attribute('value'), 'Nuevo Apellido')

    def test_editar_perfil_invalido(self):
        # Navegar a la página de editar perfil
        self.browser.get(self.live_server_url + self.url)

        # Completar el formulario con contraseña incorrecta
        self.browser.find_element(By.NAME, "email").clear()
        self.browser.find_element(By.NAME, "email").send_keys("newemail@example.com")
        self.browser.find_element(By.NAME, "first_name").clear()
        self.browser.find_element(By.NAME, "first_name").send_keys("Nuevo Nombre")
        self.browser.find_element(By.NAME, "last_name").clear()
        self.browser.find_element(By.NAME, "last_name").send_keys("Nuevo Apellido")
        self.browser.find_element(By.NAME, "current_password").send_keys("wrongpassword123")  # Contraseña incorrecta
        self.browser.find_element(By.NAME, "new_password").send_keys("newpassword123")
        self.browser.find_element(By.NAME, "confirm_new_password").send_keys("newpassword123")

        # Enviar el formulario
        submit_button = self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        self.browser.execute_script("arguments[0].click();", submit_button)

        
        # Verificar que se muestre el mensaje de error
        error_message = self.browser.find_element(By.CSS_SELECTOR, '.alert-danger')
        self.assertIn("La contraseña actual no es correcta", error_message.text)

    def tearDown(self):
        self.browser.quit()
