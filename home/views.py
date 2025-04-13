import json
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from urllib.parse import quote_plus, urlencode
from authlib.integrations.django_client import OAuth
from google import genai
import PIL.Image as Image
from bs4 import BeautifulSoup
from django.http import JsonResponse
import re

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

client = genai.Client(api_key=settings.GENAI_API_KEY)

def index(request):
    return render(
        request, 
        'home/index.html',
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
            "website_name": settings.WEBSITE_NAME,
        },
    )

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def trans_web(request):
    if request.method == "GET":
        return render(request, 'home/trans_web.html')
    elif request.method == "POST":
        data = request.FILES.get("file")
        html = None

        if data is not None:
            image = Image.open(data)
            prompt = f"""
                Translate this image to HTML, Javascript, React in that order seperated by: <!--Seperate-->
                
                Do not describe it simply just provide html for this image
                Please add comments to the code for just describing different parts of the code.
                For things that cannot be generated put a placeholder like for icons, images, etc.

                Try and make it more visually appealing if it has to
                Remove the ```html```
            """
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                prompt,
                image,
                "Identify the 2 main theme colors in css style tags"
                ]
            )
            raw_html = response.text
            cleaned = re.sub(r'^```html\s*', '', raw_html.strip(), flags=re.IGNORECASE)
            html = re.sub(r'```$', '', cleaned.strip())
            lang = html
            html = html.split('<!--Seperate-->')[0]
            print(html)
        return render(request, 'home/trans_web.html', context={
            "data": data,
            "html": html,
            "data": data,
            "lang": lang
        })

from django.http import HttpResponse
from datetime import datetime
import zipfile
import io

def download(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        selected_formats = request.POST.getlist('format')
        print(selected_formats)

        if not selected_formats or not code:
            return HttpResponse("No format or code provided.", status=400)

        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for fmt in selected_formats:
                filename = f'code.{fmt}'
                zf.writestr(filename, code)

        # Build response
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="code-{datetime.now().isoformat()}.zip"'
        return response

    