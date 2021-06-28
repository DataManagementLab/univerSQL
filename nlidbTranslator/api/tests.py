from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from rest_framework.test import force_authenticate

# Create your tests here.

class TranslationTestCase(APITestCase):

    def test_translation_with_editsql(self):
        data = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        response = self.client.post("/translate", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['translator'], "editsql")
        self.assertIsNotNone(response.data['sql_statement'])


    def test_translation_with_IRNet(self):
        data = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "IRNet"}
        response = self.client.post("/translate", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['translator'], "IRNet")
        self.assertIsNotNone(response.data['sql_statement'])





class TranslationLogsTestCase(APITestCase):

    def test_User_Authentication(self):
        response_before_authentication = self.client.get("/translate/logs")
        self.assertEqual(response_before_authentication.status_code, status.HTTP_401_UNAUTHORIZED)
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_after_authentication = self.client.get("/translate/logs")
        self.assertEqual(response_after_authentication.status_code, status.HTTP_200_OK)

    def test_Log_list_before_and_after_first_translation(self):
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_before_insertion = self.client.get("/translate/logs")
        #force_authenticate(re)
        self.assertEqual(response_before_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_before_insertion.data), 0)
        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        data_2 = {"nl_question": "Return the average earnings across all poker players.",
                "db_schema": "poker_player",
                "translator": "IRNet"}
        self.client.post("/translate", data_1)
        self.client.post("/translate", data_2)
        response_after_insertion = self.client.get("/translate/logs")
        self.assertEqual(response_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_after_insertion.data), 2)
        self.assertEqual(response_after_insertion.data[0]['id'],2 )
        self.assertEqual(response_after_insertion.data[0]['translator'], "IRNet")

        self.assertEqual(response_after_insertion.data[1]['id'], 1)
        self.assertEqual(response_after_insertion.data[1]['translator'], "editsql")

    def test_request_specific_logitem(self):
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_before_insertion = self.client.get("/translate/logs")
        response_specific_logitem = self.client.get("/translate/log_item/1")
        self.assertEqual(response_specific_logitem.status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=user)

        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        data_2 = {"nl_question": "Return the average earnings across all poker players.",
                "db_schema": "poker_player",
                "translator": "IRNet"}
        self.client.post("/translate", data_1)
        self.client.post("/translate", data_2)
        response_specific_logitem_after_insertion = self.client.get("/translate/log_item/1")
        self.assertEqual(response_specific_logitem_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(response_specific_logitem_after_insertion.data['id'], 1)
        self.assertEqual(response_specific_logitem_after_insertion.data['translator'], "editsql")

    def test_specific_number_of_logs(self):
        response_before_insertion = self.client.get("/translate/logs")
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        data_2 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        data_3 = {"nl_question": "Return the average earnings across all poker players.",
                "db_schema": "poker_player",
                "translator": "IRNet"}
        data_4 = {"nl_question": "Return the average earnings across all poker players.",
                "db_schema": "poker_player",
                "translator": "editsql"}

        self.client.post("/translate", data_1)
        self.client.post("/translate", data_2)
        self.client.post("/translate", data_3)
        self.client.post("/translate", data_4)

        response_all_logs_after_insertion = self.client.get("/translate/logs")
        self.assertEqual(response_all_logs_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_all_logs_after_insertion.data), 4)

        response_2_logs_after_insertion = self.client.get("/translate/logs/2")
        self.assertEqual(response_2_logs_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_2_logs_after_insertion.data), 2)

    def test_delete_logging(self):
        response_before_insertion = self.client.get("/translate/logs")
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        data = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                  "db_schema": "car_1",
                  "translator": "editsql"}
        response = self.client.post("/translate", data)
        log_id = response.data['id']
        response_before_deletion = self.client.get("/translate/log_item/"+str(log_id), data)
        self.assertEqual(response_before_deletion.status_code, status.HTTP_200_OK)
        resonse_deletion = self.client.delete("/translate/log_item/"+str(log_id))
        self.assertEqual(resonse_deletion.status_code, status.HTTP_204_NO_CONTENT)
        response_after_deletion = self.client.get("/translate/log_item/" + str(log_id), data)
        self.assertEqual(response_after_deletion.status_code, status.HTTP_404_NOT_FOUND)


class TranslatorsListTestCase(APITestCase):
    def test_get_translators_List(self):
        response = self.client.get("/translators")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SchemasTestCase(APITestCase):
    def test_get_schema_List(self):
        response = self.client.get("/schemas")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if(len(response.data)>0):
            specific_schema = response.data[0]
            response_specific_schema = self.client.get("/schemas/"+ str(specific_schema))
            self.assertEqual(response_specific_schema.status_code, status.HTTP_200_OK)
        else:
            response_specific_schema_without_entries =  self.client.get("/schemas/test")
            self.assertEqual(response_specific_schema_without_entries.status_code, status.HTTP_404_NOT_FOUND)


class InteractionTestCase(APITestCase):

    def test_start_interaction(self):
        data = {
              "nl_question": "What is the birth date of each poker player?",
                "db_schema": "poker_player",
                "translator": "editsql"
        }
        response = self.client.post("/interaction", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_started_interaction(self):
        data = {
              "nl_question": "What is the birth date of each poker player?",
                "db_schema": "poker_player",
                "translator": "editsql"
        }
        response = self.client.post("/interaction", data)
        interaction_id = response.data['interaction_id']
        response_interaction_id = self.client.get('/interaction/' + str(interaction_id))
        self.assertEqual(response_interaction_id.status_code, status.HTTP_200_OK)
        self.assertEqual(response_interaction_id.data['interaction_id'], interaction_id)
        self.assertEqual(response_interaction_id.data['url'], response.data['url'])


    def test_continue_started_interaction(self):
        data_1 = {
            "nl_question": "What is the birth date of each poker player?",
            "db_schema": "poker_player",
            "translator": "editsql"
        }
        data_2 = {
            "nl_question": "Sort the list by the poker player's earnings."
        }
        response = self.client.post("/interaction", data_1)
        interaction_id = response.data['interaction_id']
        response_interaction_id = self.client.get('/interaction/' + str(interaction_id))
        response_continue_interaction = self.client.post("/interaction/" + str(interaction_id), data_2 )
        self.assertEqual(response_continue_interaction.status_code, status.HTTP_200_OK)

class InteractionLogsTestCase(APITestCase):

    def test_User_Authentication(self):
        response_before_authentication = self.client.get("/interaction/logs")
        self.assertEqual(response_before_authentication.status_code, status.HTTP_401_UNAUTHORIZED)
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_after_authentication = self.client.get("/interaction/logs")
        self.assertEqual(response_after_authentication.status_code, status.HTTP_200_OK)

    def test_Log_list_before_and_after_first_translation(self):
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_before_insertion = self.client.get("/interaction/logs")
        self.assertEqual(response_before_insertion.status_code, status.HTTP_200_OK)

        data = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        self.client.post("/interaction", data)
        response_after_insertion = self.client.get("/interaction/logs")
        self.assertEqual(response_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_after_insertion.data), 1)
        self.assertEqual(response_after_insertion.data[0]['translator'], "editsql")


    def test_request_specific_logitem(self):
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        response_before_insertion = self.client.get("/interaction/logs")
        response_specific_logitem = self.client.get("/interaction/log_item/0")
        self.assertEqual(response_specific_logitem.status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=user)
        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        self.client.post("/interaction", data_1)
        response_specific_logitem_after_insertion = self.client.get("/interaction/log_item/0")
        self.assertEqual(response_specific_logitem_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(response_specific_logitem_after_insertion.data['interaction_id'], 0)
        self.assertEqual(response_specific_logitem_after_insertion.data['translator'], "editsql")

    def test_specific_number_of_logs(self):
        response_before_insertion = self.client.get("/interaction/logs")
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        data_2 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        self.client.post("/interaction", data_1)
        self.client.post("/interaction", data_2)

        response_all_logs_after_insertion = self.client.get("/interaction/logs")
        self.assertEqual(response_all_logs_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_all_logs_after_insertion.data), 2)

        response_1_logs_after_insertion = self.client.get("/interaction/logs/1")
        self.assertEqual(response_1_logs_after_insertion.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_1_logs_after_insertion.data), 1)

    def test_delete_logging(self):
        user = User.objects.create_user(username='testUser')
        self.client.force_authenticate(user=user)
        data_1 = {"nl_question": "What is the number of cars with more than 4 cylinders?",
                "db_schema": "car_1",
                "translator": "editsql"}
        response = self.client.post("/interaction", data_1)
        log_id = response.data['interaction_id']
        response_before_deletion = self.client.get("/interaction/log_item/" + str(log_id))
        self.assertEqual(response_before_deletion.status_code, status.HTTP_200_OK)
        response_deletion = self.client.delete("/interaction/log_item/" + str(log_id))
        response_after_deletion = self.client.get("/interaction/log_item/" + str(log_id))
        self.assertEqual(response_after_deletion.status_code, status.HTTP_404_NOT_FOUND)
