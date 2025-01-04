from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from authentication.models import UserProfile
from Easier import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        mainLevel = request.POST['mainLevel']
        subLevel = request.POST['subLevel']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        # Vérifier si le nom d'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another username.")
            return redirect('home')
        
        # Vérifier si l'email est déjà enregistré
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('home')
        
        # Vérifier la longueur du nom d'utilisateur
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!")
            return redirect('home')
        
        # Vérifier si les mots de passe correspondent
        if pass1 != pass2:
            messages.error(request, "Passwords do not match!")
            return redirect('home')
        
        # Vérifier si le nom d'utilisateur est alphanumérique
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('home')
        
        # Créer l'utilisateur
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False  # Garder l'utilisateur inactif jusqu'à la confirmation de l'email
        myuser.save()
        
        # Créer le profil utilisateur
        profile = UserProfile(user=myuser, main_level=mainLevel, sub_level=subLevel)
        profile.save()

        messages.success(request, "Your account has been created successfully! Please check your email to confirm your email address to activate your account.")
        
        # Envoyer un email de bienvenue
        subject = "Welcome to Easier!!"
        message = f"Hello {myuser.first_name}!! \nWelcome to Easier!! \nThank you for visiting our website. We have also sent you a confirmation email, please confirm your email address."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Envoyer un email de confirmation d'adresse email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Easier Login!!"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
        
    return render(request, "authentication/signup.html")


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        remember_me = request.POST.get('remember_me', None)
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', 'home')
            response = redirect(next_url)
            if remember_me:
                response.set_cookie('username', username, max_age=1209600)
            else:
                response.set_cookie('username', username)

            return response
        else:
            return redirect('home')
    
    next_url = request.POST.get('next', 'home')
    return render(request, "authentication/signin.html", {'next': next_url})


def signout(request):
    logout(request)
    return redirect('home')


def contact(request):
    return render(request, "authentication/contact.html")


@login_required(login_url='/signin')
def cours(request):
    return render(request, "cours/cours_etr_résumés.html")

def formation(request):
    return render(request, "authentication/formation.html")

@login_required(login_url='/signin')
def math(request):
    user_profile = request.user.userprofile

    if user_profile.sub_level in ['mpsi','psi','ptsi','tsi_1','mp','tsi_2']:
        pdf_url = '/media/pdfs/Math/Résumé_Analyse_SUP_SPE.pdf'
        pdf_url2 = None
    elif user_profile.sub_level in ['tronc_comm_sci','tronc_comm_tech']:
        pdf_url2 = '/media/pdfs/Math/Résumé-ensembles-de-nombres-arithmétiques.pdf'
        pdf_url = None
    else:
         pdf_url = None
         pdf_url2 = None

    context = {
        'pdf_url': pdf_url,
        'pdf_url2':pdf_url2,
    }

    return render(request, 'cours/math.html', context)

@login_required(login_url='/signin')
def Physique(request):
    user_profile = request.user.userprofile
    if user_profile.sub_level in ['mpsi','psi','ptsi','tsi_1','mp','tsi_2']:
        pdf_url = '/media/pdfs/Physique/Résumé_électromagnétisme_SUP_SPE.pdf'
        pdf_url2 = 'Résumé_Thermodynamique_SUPSPE'
        pdf_url3 = None
    elif user_profile.sub_level in ['science_math','science_experimental','science_et_techno_ele1','science_et_techno_meca1']:
        pdf_url3 = '/media/pdfs/Physique/Travail_et_énergie_potentielle_de_pesanteur.pdf'
    else:
        pdf_url = None
        pdf_url2 = None
        pdf_url3 = None
        

    context = {
        'pdf_url': pdf_url,
        'pdf_url2': pdf_url2,
        'pdf_url3' : pdf_url3
    }

    return render(request, "cours/Physique.html", context)


@login_required(login_url='/signin')
def Chimie(request):
    user_profile = request.user.userprofile
    if user_profile.sub_level in ['mpsi','psi','ptsi','tsi_1','mp','tsi_2']:
        pdf_url = '/media/pdfs/Chimie/Résumé_THERMOCHIMIE.pdf'
    else:
        pdf_url = None

    context = {
        'pdf_url': pdf_url,
    }
    return render(request, "cours/Chimie.html",context)

@login_required(login_url='/signin')
def Si(request):
    user_profile = request.user.userprofile
    if user_profile.sub_level in ['tsi_1']:
        pdf_url = '/media/pdfs/SI/Résumé_Réseau_triphasé_équilibré.pdf'
        pdf_url2 = '/media/pdfs/SI/Synthèse_étude_statique.pdf'
    elif user_profile.sub_level in ['science_et_techno_ele2']:
        pdf_url = '/media/pdfs/SI/Résumé_Réseau_triphasé_équilibré.pdf'
    elif user_profile.sub_level in ['science_et_techno_meca2','science_et_techno_meca1','mpsi','ptsi']:
        pdf_url = '/media/pdfs/SI/Synthèse_étude_statique.pdf'
    else:
        pdf_url = None
        pdf_url2 = None

    context = {
        'pdf_url': pdf_url,
        'pdf_url2': pdf_url2
    }
    return render(request, "cours/Si.html",context)
    


@login_required(login_url='/signin')
def Fr(request):
    return render(request, "cours/Fr.html")

@login_required(login_url='/signin')
def An(request):
    return render(request, "cours/An.html")

@login_required(login_url='/signin')
def Info(request):

    user_profile = request.user.userprofile
    if user_profile.sub_level in ['mpsi','psi','ptsi','tsi_1','mp','tsi_2']:
        pdf_url = '/media/pdfs/Info/Résumé_info_SUP_SPE.pdf'
    else:
        pdf_url = None

    context = {
        'pdf_url': pdf_url,
    }

    return render(request, "cours/Info.html", context)