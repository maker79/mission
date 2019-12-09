from django.test import TestCase
from selenium import webdriver
from .forms import HashForm
import hashlib
from .models import Hash
from django.core.exceptions import ValidationError
import time

# Create your tests here.
class FunctionalTestCase(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_there_is_homepage(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('enter hash here:', self.browser.page_source)

    def test_hash_of_hello(self):
        self.browser.get('http://localhost:8000')
        text = self.browser.find_element_by_id('id_text')
        text.send_keys('hello')
        self.browser.find_element_by_name('submit').click()
        self.assertIn('2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower(), self.browser.page_source)

    def test_hash_ajax(self):
        self.browser.get('http://localhost:8000')
        text = self.browser.find_element_by_id('id_text')
        text.send_keys('hello')
        time.sleep(5) # wait for AJAX
        self.assertIn('2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower(), self.browser.page_source)

    def tearDown(self):
        self.browser.quit()

class UnitTestCase(TestCase):

    def test_home_homepage_template(self):
        resopnse = self.client.get('/')
        self.assertTemplateUsed(resopnse, 'hashing/home.html')

    def test_hash_form(self):
        form = HashForm(data={'text':'hello'})
        self.assertTrue(form.is_valid())

    def test_hash_func_works(self):
        text_hash = hashlib.sha256('hello'.encode('utf-8')).hexdigest()
        self.assertEqual('2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower(), text_hash)

    def saveHash(self):
        hash = Hash()
        hash.text = 'hello'
        hash.hash = '2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower()
        hash.save()
        return hash

    def test_hash_object(self):
        hash = self.saveHash()
        pulled_hash = Hash.objects.get(hash='2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower())
        self.assertEqual(hash.text, pulled_hash.text)

    def test_viewing_hash(self):
        hash = self.saveHash()
        response = self.client.get('/hash/2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824'.lower())
        self.assertContains(response, 'hello')

    def test_bad_data(self):
        def badHash():
            hash = Hash()
            hash.hash = '2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824ggggggg'.lower()
            hash.full_clean()
        self.assertRaises(ValidationError, badHash)
