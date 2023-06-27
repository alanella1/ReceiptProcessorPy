import unittest
from server import *

payload = {
    "retailer": "Target",
    "purchaseDate": "2023-06-20",
    "purchaseTime": "10:30",
    "total": "16.98",
    "items": [
        {"shortDescription": "Item 1", "price": "10.99"},
        {"shortDescription": "Item 2", "price": "5.99"},
    ],
}
curID = ""


class FlaskAppTests(unittest.TestCase):
    curID = ""

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_bad_receipt_post(self):
        this_payload = payload
        del this_payload["total"]
        response = self.app.post(
            "/receipts/process",
            data=json.dumps(this_payload),
            content_type="application/json",
        )
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", data)

    def test_post_receipt(self):
        payload["total"] = "16.98"
        response = self.app.post(
            "/receipts/process",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", data)
        self.__class__.curID = data["id"]

    def test_get_receipt_points(self):
        response = self.app.get(f"/receipts/{self.__class__.curID}/points")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("points", data)

    def test_get_receipt_points_not_found(self):
        receipt_id = "non-existent-id"
        response = self.app.get(f"/receipts/{receipt_id}/points")
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 404)
        self.assertIn("description", data)

    def test_retailer_points(self):
        six_points = "Target"
        one_point = "F"
        self.assertEqual(getRetailerPoints(six_points), 6)
        self.assertEqual(getRetailerPoints(one_point), 1)

    def test_total_points(self):
        seven_five = "9.00"
        twen_five = "5.75"
        zero = "5.55"
        self.assertEqual(getTotalPoints(seven_five), 75)
        self.assertEqual(getTotalPoints(twen_five), 25)
        self.assertEqual(getTotalPoints(zero), 0)

    def test_items_points(self):
        multiple = "xxx            "
        price = "9.01"
        who_cares = "stuff"
        price_2 = "100.00"
        item_1 = Item(multiple, price)
        item_2 = Item(who_cares, price_2)

        self.assertEqual(getItemsPoints([item_1, item_2]), 7)

    def test_day_points(self):
        evenDate = "1999-05-02"
        self.assertEqual(getDayPoints(evenDate), 0)

        oddDate = "1999-05-03"
        self.assertEqual(getDayPoints(oddDate), 6)

    def test_time_points(self):
        nope = "14:00"
        yep = "14:01"
        nope_2 = "16:00"
        self.assertEqual(getTimePoints(nope), 0)
        self.assertEqual(getTimePoints(yep), 10)
        self.assertEqual(getTimePoints(nope_2), 0)

    def test_valid_date(self):
        yep = "1999-12-25"
        dne = "1999-13-15"
        num = 1999
        self.assertTrue(validateDate(yep))
        self.assertFalse(validateDate(dne))
        self.assertFalse(validateDate(num))

    def test_valid_retailer(self):
        yep = "l;askdfjl;kasjgl;kwej%%$%(#$*&(%*&))"
        nope = 5

        self.assertTrue(validateRetailer(yep))
        self.assertFalse(validateRetailer(nope))

    def test_valid_time(self):
        yep = "23:59"
        dne = "11:70"
        nope = 50

        self.assertTrue(validateTime(yep))
        self.assertFalse(validateTime(dne))
        self.assertFalse(validateTime(nope))

    def test_valid_items(self):
        good_desc = "anything here"
        bad_desc = " any,leading space"
        good_price = "14.55"
        bad_price = "14"
        good_1 = {"shortDescription": good_desc, "price": good_price}
        bad_1 = {"shortDescription": bad_desc, "price": good_price}
        bad_2 = {"shortDescription": good_desc, "price": bad_price}

        self.assertIsInstance(validateItems([good_1, good_1])[0], Item)
        self.assertFalse(validateItems([good_1, bad_1]))
        self.assertFalse(validateItems([good_1, bad_2]))
        self.assertFalse(validateItems([]))


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FlaskAppTests("test_bad_receipt_post"))
    suite.addTest(FlaskAppTests("test_post_receipt"))
    suite.addTest(FlaskAppTests("test_get_receipt_points"))
    suite.addTest(FlaskAppTests("test_get_receipt_points_not_found"))
    suite.addTest(FlaskAppTests("test_retailer_points"))
    suite.addTest(FlaskAppTests("test_total_points"))
    suite.addTest(FlaskAppTests("test_items_points"))
    suite.addTest(FlaskAppTests("test_day_points"))
    suite.addTest(FlaskAppTests("test_time_points"))
    suite.addTest(FlaskAppTests("test_valid_date"))
    suite.addTest(FlaskAppTests("test_valid_retailer"))
    suite.addTest(FlaskAppTests("test_valid_time"))
    suite.addTest(FlaskAppTests("test_valid_items"))
    unittest.TextTestRunner().run(suite)
