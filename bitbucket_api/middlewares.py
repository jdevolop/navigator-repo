# https://bitbucket.org/account/user/%7B86690619-6ad0-4469-9e21-1110c5104bc5%7D/oauth-consumers#access_token=qSgYshkh9OdInqtGUnR0TsU3MTKpJSDXZtmk0edocmI0vHSjxBpicWgVramUqrbkalTawSFahidUKSQ3bik%3D&scopes=pullrequest+account&expires_in=7200&token_type=bearer
# https://bitbucket.org/account/user/%7B86690619-6ad0-4469-9e21-1110c5104bc5%7D/oauth-consumers?code=9Szr6y3BdHHCC56wnS
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseNotFound, JsonResponse
import requests, json, datetime, csv
from .views import bit_parser, com_filter, update_access, get_token

update_access()


def get_repos(un):
    s_resp = requests.get('https://bitbucket.org/!api/2.0/repositories/{un}?sort=-updated_on&access_token={token}'.format(un=un, token=get_token()))
    return s_resp

def get_commit(un, slug):
    resp = requests.get('https://bitbucket.org/!api/2.0/repositories/{un}/{slug}/commits?sort=-updated_on&access_token={token}'.format(un=un, slug=slug, token=get_token()))
    return resp

def search(request, un):
    s_resp = get_repos(un)
    s_res = s_resp.json()
    if s_resp.status_code == 200:
        s_filtered = bit_parser(s_res)
        s_r = JsonResponse(data=s_filtered)
        s_r['Content-Type'] = 'application/json; charset=utf-8'
        s_r['Access-Control-Allow-Origin'] = '*'
        return s_r
    elif s_resp.status_code == 401:
        update_access()
        res = get_repos(un)
        filtered = bit_parser(res)
        r = JsonResponse(data=filtered)
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r
    elif s_resp.status_code == 404:
        r = HttpResponseNotFound(json.dumps({"message": "Not Found"}))
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r
    else:
        r = HttpResponseServerError(json.dumps({'message': "Something wrong"}))
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r

def commit(request, un, slug):
    resp = get_commit(un, slug)
    res = resp.json()
    if resp.status_code == 200:
        filtered = com_filter(res)
        r = JsonResponse(data=filtered)
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r
    elif resp.status_code == 401:
        update_access()
        resp = get_commit(un, slug)
        filtered = com_filter(resp)

        if filtered['message'] == 'Not Found':
            r = HttpResponseNotFound(json.dumps(filtered))
            r['Content-Type'] = 'application/json; charset=utf-8'
            r['Access-Control-Allow-Origin'] = '*'
            return r

        r = JsonResponse(data=filtered)
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r
    elif resp.status_code == 404:
        r = HttpResponseNotFound(json.dumps({"message": "Not Found"}))
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r    
    else:
        r = HttpResponseServerError(json.dumps({'message': "Something wrong"}))
        r['Content-Type'] = 'application/json; charset=utf-8'
        r['Access-Control-Allow-Origin'] = '*'
        return r   


def download_as_csv(request):
    un = request.GET.get('username')
    req = requests.get(f'http://127.0.0.1/bitbucket/api/search/{un}/repos/')
    
    if req.status_code == 200:    
        data = req.json()['data']
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="result_bitbucket_{datetime.datetime.now():%Y-%m-%d}.csv"'

        w = csv.writer(resp)
        w.writerow(['full_name', 'html_url', 'description', 'language', 'updated_at', 'is_private'])

        for repo in data:
            w.writerow([repo['full_name'], repo['html_url'], repo['description'], repo['language'], repo['updated_at'], repo['is_private']])

        return resp
    else:
        return HttpResponseNotFound('Not Found')    