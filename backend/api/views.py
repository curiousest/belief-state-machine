# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .crew.main import extract_beliefs, write_parable

class ExtractBeliefsView(APIView):
    def post(self, request):
        text = request.data.get('text')
        author_background = request.data.get('author_background')

        beliefs = extract_beliefs(text, author_background).to_dict()['beliefs']

        return Response({'beliefs': beliefs})

class GenerateParableView(APIView):
    def post(self, request):
        belief = request.data.get('belief')
        action = request.data.get('action')  # 'changed' or 'reinforced' or 'meaningless'
        text = request.data.get('text')
        context = request.data.get('author_background')
        assert action in ["changed", "reinforced", "meaningless"]

        parable = write_parable(belief, action, text, context)

        return Response({'parable': str(parable)})
