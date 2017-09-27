from flask_praetorian.exceptions import PraetorianError


class TestPraetorianError:

    def test_jsonify(self):
        try:
            raise PraetorianError('some message')
        except PraetorianError as err:
            response = err.jsonify()
            assert 'some message' in response.json['message']
            assert response.json['status_code'] == 401
            assert response.status_code == 401

        try:
            raise PraetorianError('some message', status_code=403)
        except PraetorianError as err:
            response = err.jsonify()
            assert 'some message' in response.json['message']
            assert response.json['status_code'] == 403
            assert response.status_code == 403

        try:
            raise PraetorianError('some message', status_code=403)
        except PraetorianError as err:
            response = err.jsonify(status_code=404, message='custom message')
            assert response.json['message'] == 'custom message'
            assert response.json['status_code'] == 404
            assert response.status_code == 404
