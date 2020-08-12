from django.shortcuts import *
from django.core.urlresolvers import reverse
from map.models import *
from django.contrib.auth.models import User
from django.views.generic import View, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.gis.geos import Point, GeometryCollection, Polygon, MultiPolygon, GEOSGeometry
import json
from django import forms


class TagForm(forms.Form):
    name = forms.CharField(label='Tag Name', max_length=100)
#    description = forms.CharField(label='Tag Description')

# Create your views here.
def index(request):
    users = User.objects.all()
    zones = Zone.objects.order_by('name')
    context= {'zones': zones, 'users' : users}
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse(user_map, args=[request.user.id]))
    else:
        return render(request, 'map/homepage.html', {'context': context})

def user_map(request, usr):
    users = User.objects.all()
    if not request.user.is_staff:
        if int(request.user.id) != int(usr):
            return HttpResponseRedirect('/')
                        
    zones = Zone.objects.filter(author_id=usr).order_by('name')
    
    context= {'zones': zones, 'user' : usr, 'users' : users}
    context['user_page'] = True
    
    
    if 'longitude' in request.session:
        context['longitude'] = request.session['longitude']
        context['latitude'] = request.session['latitude']
        context['zoom'] = request.session['zoom']

    return render(request, 'map/homepage.html', {'context': context})

def user_redr(request):
	return HttpResponseRedirect(
               reverse(user_map,
                       args=[request.user.id]))

def view_user_map(request, usr):
	users = User.objects.all()
	zones = Zone.objects.filter(author_id=usr).order_by('name')
	author = User.objects.filter(id=usr).first()
	context= {'zones': zones, 'user' : usr, 'users' : users, 'author' : author}

	if 'longitude' in request.session:
		context['longitude'] = request.session['longitude']
		context['latitude'] = request.session['latitude']
		context['zoom'] = request.session['zoom']


	return render(request, 'map/view_map.html', {'context': context})

def view_all_map(request):
	users = User.objects.all()
	zones = Zone.objects.all()
	context= {'zones': zones, 'users' : users}

	if 'longitude' in request.session:
		context['longitude'] = request.session['longitude']
		context['latitude'] = request.session['latitude']
		context['zoom'] = request.session['zoom']

	return render(request, 'map/homepage.html', {'context': context})

def view_all_zones_list(request):
	context = {}
	zones = Zone.objects.order_by('name')
	context['zones'] = zones
	context['title'] = 'View All Zones by All Users'

	return render(request, 'map/zones.html', {'context' : context})

def view_user_zones_list(request, usr):
	context = {}
	user = User.objects.filter(id=usr).first()
	zones = Zone.objects.filter(author=user).order_by('name')
	context['zones'] = zones
	context['title'] = 'View All Zones by ' + user.username
	context['user_page'] = True
	return render(request, 'map/zones.html', {'context' : context})


class ZoneView(DetailView):
    model = Zone
    template_name = 'map/zoneview.html'

    def get_context_data(self, **kwargs):
        context = super(ZoneView, self).get_context_data(**kwargs)
        if 'longitude' in self.request.session:
		context['longitude'] = self.request.session['longitude']
		context['latitude'] = self.request.session['latitude']
		context['zoom'] = self.request.session['zoom']

    	context['tags'] = Tag.objects.all()



    	context['users'] = User.objects.all()

    	geojson = json.loads(self.object.geom.geojson)

    	geometries_length = len(geojson["geometries"][0]["coordinates"])

    	if geometries_length > 1:
    		context['ghost'] = True

    	return context



@staff_member_required
@login_required(login_url='/account/login/')
def tag_form(request):
	users = User.objects.all()
	tags = Tag.objects.all()

	if request.method == 'POST':
		form = TagForm(request.POST)

		if form.is_valid():
			tag_name = request.POST['name']
			# tag_description = request.POST['description']

			tag_check = Tag.objects.filter(name=tag_name).first()

			if tag_check != None:
				print "Tag Exists..."
			else:
				new_tag = Tag()
				new_tag.name = tag_name
				new_tag.description = ""
				new_tag.save()

			return HttpResponseRedirect('/tag-form/')
	else:
		form = TagForm()


		return render(request, 'map/tagform.html', {'form': form, 'tags' : tags, 'users' : users})

def delete_tag(request, number):

	tag = Tag.objects.filter(id=number).first()

	if tag != None:
		tag.delete()
	else:
		pass

	return HttpResponseRedirect('/tag-form/')

def location_session_data(request, a, b, c):
	request.session['latitude'] = float(a)
	request.session['longitude'] = float(b)
	request.session['zoom'] = int(c)
	return HttpResponseRedirect('/userpage/')

def delete_zone(request, number):
	zone = Zone.objects.filter(id=number).first()

	if zone != None:
		zone.delete()
	else:
		pass

	return HttpResponseRedirect('/userpage/')

def get_zone_json_user(request, usrid):
        geo = {"type" : "FeatureCollection", "features" : []}
        for i, zone in enumerate(Zone.objects.filter(author_id=usrid)):
                geojson = json.loads(zone.geom.geojson)

                print geojson['geometries']

                for i, feature in enumerate(geojson["geometries"]):
	                featureDict = {"id": zone.id, "type" : "Feature", "properties" : "", "geometry" : "", "author_id" : zone.author_id}


	                co_ords = geojson["geometries"][i]['coordinates']
	                shape_type = geojson["geometries"][i]['type']


	                featureDict["properties"] = { "fillColor" : str(zone.colour), "color" : str(zone.colour) }
	                featureDict["geometry"] = {"type" : shape_type, "coordinates" : co_ords}

	                featureDict["tags"] = []

	                tags = ZoneTag.objects.filter(zone=zone).all()

	                for tag in tags:
	                	featureDict["tags"].append([tag.tag.id, tag.tag.name, tag.tag.alias])

	                if zone.name > 0:
	                	featureDict["name"] = zone.name
	                else:
	                	featureDict["name"] = None

	                geo["features"].append(featureDict)
	                geo["author_id"] = zone.author_id

                # Why only one?

        return HttpResponse(json.dumps(geo), content_type='application/json')

def get_zone_json(request):
        geo = {"type" : "FeatureCollection", "features" : []}
        for i, zone in enumerate(Zone.objects.all()):
                geojson = json.loads(zone.geom.geojson)

                featureDict = {"id": zone.id, "type" : "Feature", "properties" : "", "geometry" : "", "author_id" : zone.author_id}


                co_ords = geojson["geometries"][0]['coordinates']


                shape_type = geojson["geometries"][0]['type']

                featureDict["properties"] = { "fillColor" : str(zone.colour), "color" : str(zone.colour) }
                featureDict["geometry"] = {"type" : shape_type, "coordinates" : co_ords}

                featureDict["tags"] = []

                tags = ZoneTag.objects.filter(zone=zone).all()

                for tag in tags:
                	featureDict["tags"].append([tag.tag.id, tag.tag.name])

                if zone.name > 0:
                	featureDict["name"] = zone.name
                else:
                	featureDict["name"] = None

                geo["features"].append(featureDict)


        return HttpResponse(json.dumps(geo), content_type='application/json')



def send_zone_json(request):
	if request.method == 'POST':

                print("000")

		sh = json.loads(request.POST.get('shapes', ''))

                print(sh)

		try:
			shape = sh[0]
		except KeyError:
			shape = sh

		ghost = json.loads(request.POST.get('ghost', ''))

		print("Shapes", shape)
		print("Ghost Zone", ghost)

		try:
			existing_zone = Zone.objects.filter(id=shape['id']).first()
		except KeyError:
			z = Zone()
		else:
			if existing_zone != None:
				z = existing_zone
			else:
				z = Zone()

                print(1)

		try:
			colour = shape['properties']['color']
		except KeyError:
			colour = 'none'

		try:
			print shape['name']
		except KeyError:
			pass
		else:
			z.name = shape['name']

                print(2)

		try:
			tags_in = shape['tags_in']
			tags_out = shape['tags_out']
		except KeyError:
			pass
		else:
			for t_i in tags_in:
				tag = Tag.objects.filter(id=t_i).first()
				if ZoneTag.objects.filter(zone=z, tag=tag).first() != None:
					pass
				else:
					new_tag_in = ZoneTag(zone=z, tag=tag)
					new_tag_in.save()

			for t_o in tags_out:
				tag = Tag.objects.filter(id=t_o).first()

				if ZoneTag.objects.filter(zone=z, tag=tag).first() == None:
					pass
				else:
					new_tag_out = ZoneTag.objects.filter(zone=z, tag=tag).first()
					new_tag_out.delete()

                print(3)
		co_ords = GEOSGeometry(json.dumps(shape['geometry']))

                print(4)

		if "features" in ghost:
			ghost_co_ords = GEOSGeometry(json.dumps(ghost["features"][0]["geometry"]))
			z.geom = GeometryCollection(co_ords, ghost_co_ords)
			print z.geom.json

		else:
			z.geom = GeometryCollection(co_ords)



		z.colour = colour
		z.author = request.user
		z.save()


	return  HttpResponse(json.dumps(shape))

def export_zone(zone):
        # build a list of names of all the tags for this zone
        tags = map(lambda t: t.tag.name, ZoneTag.objects.filter(zone=zone))

        # vertices is a list of lists of points
        # (so we can form ghost zones with two lists)
        vertices = []

        geojson = json.loads(zone.geom.geojson)

        # check for multiple polygons that they are the same
        # number of points each, if not reduce to smallest size
        smallest = 99999
        for points in geojson["geometries"]:
                print(points["coordinates"][0])
                if len(points["coordinates"][0])<smallest:
                        smallest = len(points["coordinates"][0])

        #print("smallest is "+str(smallest))

        for points in geojson["geometries"]:
                if len(points["coordinates"][0])>smallest:
                        #print("reducing from "+str(len(points["coordinates"][0])))
                        try: vertices.append(map(lambda p:{"lng":p[0],"lat":p[1]},points["coordinates"][0][:smallest]))
                        except: pass
                        else: continue
                else:
                        try: vertices.append(map(lambda p:{"lng":p[0],"lat":p[1]},points["coordinates"][0]))
                        except: pass
                        else: continue

        bike_zone = {"id" : zone.id,
                     "mapid" : 0, # probably not used
                     "name" : zone.name,
                     "color" : zone.colour,
                     "categories" : tags,
                     "vertices" : vertices}

        return bike_zone;

def get_bike_json(request):
        # export to format expected by swamp bike system
        bike_map = {"id" : 0,
                    "name" : "map",
                    "zones" : []}

        for i, zone in enumerate(Zone.objects.all()):
                bike_map["zones"].append(export_zone(zone));

        response = HttpResponse(json.dumps([bike_map]), content_type='text/json')
        response['Content-Disposition'] = 'attachment; filename="map.json"'
        return response



def get_bike_json_user(request, user):
        # export to format expected by swamp bike system
        bike_map = {"id" : 0,
                    "name" : "map",
                    "zones" : []}

        for i, zone in enumerate(Zone.objects.filter(author_id=user)):
                bike_map["zones"].append(export_zone(zone));


        response = HttpResponse(json.dumps([bike_map]), content_type='text/json')
        response['Content-Disposition'] = 'attachment; filename="map.json"'
        return response

