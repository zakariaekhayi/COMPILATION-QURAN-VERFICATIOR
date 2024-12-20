import re
from flask import Flask, request, render_template_string
import ply.lex as lex
import ply.yacc as yacc
from difflib import get_close_matches

app = Flask(__name__)

# Liste des versets corrects
versets_corrects = [
    "بسم الله الرحمن الرحيم", 
    "الحمد لله رب العالمين", 
    "الرحمن الرحيم"," ملك يوم الدين",
    "إياك نعبد وإياك نستعين",
    "اهدنا الصراط المستقيم",
    "صراط الذين أنعمت عليهم غير",  
    "المغضوب عليهم ولا الضالين"  
]





# Définition des tokens pour chaque mot de la sourate Al-Fatiha
# Define your tokens here (e.g., BISM, ALLAH, ALRAHMAN)
# Liste des tokens
tokens = (
    'BISM', 'ALLAH', 'ALRAHMAN', 'ALRAHEEM', 
    'ALHAMDU', 'LILLAH', 'RABB', 'ALALAMEEN','ALRAHMAN', 'ALRAHEEM',
    'MALIKI', 'YAUM', 'ALDEEN', 'IYYAKA', 
    'NABUDU', 'WA', 'NAASTA3EEN', 'IHDINA', 
    'ALSIRAT', 'ALMOSTAQEEM', 'SIRAT', 'ALLATHEEN', 
    'AN3AMTA', 'ALAYHIM', 'GHAYR', 'ALMAGHDOUBI', 
    'WALA', 'ALDAALEEN'
)

# Expressions régulières pour chaque mot
t_BISM = r'بسم'
t_ALLAH = r'الله'
t_ALRAHMAN = r'الرحمن'
t_ALRAHEEM = r'الرحيم'
t_ALHAMDU = r'الحمد'
t_LILLAH = r'لله'
t_RABB = r'رب'
t_ALALAMEEN = r'العالمين'
t_MALIKI = r'مالك'
t_YAUM = r'يوم'
t_ALDEEN = r'الدين'
t_IYYAKA = r'إياك'
t_NABUDU = r'نعبد'
t_WA = r'و'
t_NAASTA3EEN = r'نستعين'
t_IHDINA = r'اهدنا'
t_ALSIRAT = r'الصراط'
t_ALMOSTAQEEM = r'المستقيم'
t_SIRAT = r'صراط'
t_ALLATHEEN = r'الذين'
t_AN3AMTA = r'أنعمت'
t_ALAYHIM = r'عليهم'
t_GHAYR = r'غير'
t_ALMAGHDOUBI = r'المغضوب'
t_WALA = r'ولا'
t_ALDAALEEN = r'الضالين'

# Ignorer les espaces et les diacritiques
t_ignore = ' \t\n'

# Fonction pour ignorer les diacritiques arabes
def t_ignore_TASHKEEL(t):
    r'[ًٌٍَُِّْ]'  # Regex pour les voyelles courtes
    t.lexer.skip(1)  # Ignore un caractère correspondant à l'expression régulière

# Suppression des espaces et caractères invisibles supplémentaires
def t_ignore_WHITESPACE(t):
    r'\s+'  # Ignore les espaces, tabulations et nouvelles lignes
    t.lexer.skip(len(t.value))  # Ignore ces caractères


# Gestion des erreurs lexicales
def t_error(t):
    raise Exception(f"⚠️ لديك خطأ لغوي في النص.")

# Construire le lexer
lexer = lex.lex()

# Règles syntaxiques pour la sourate Al-Fatiha
# Règles syntaxiques pour la sourate Al-Fatiha (sans retour à la ligne)
# Règles syntaxiques pour une phrase (p_phrase)
def p_phrase(p):###meme l'action semantique est verifie ici car il nous dit que les mots qui reste grace a la fonction verifier les mots manquantes 
    '''phrase : BISM ALLAH ALRAHMAN ALRAHEEM ALHAMDU LILLAH RABB ALALAMEEN ALRAHMAN ALRAHEEM MALIKI YAUM ALDEEN IYYAKA NABUDU WA IYYAKA NAASTA3EEN IHDINA ALSIRAT ALMOSTAQEEM SIRAT ALLATHEEN AN3AMTA ALAYHIM GHAYR ALMAGHDOUBI ALAYHIM WALA ALDAALEEN'''
    p[0] = "✅ النص صحيح: السورة مكتوبة بشكل صحيح!"  # Message de confirmation

def p_aya1(p):
    '''aya1 : BISM ALLAH ALRAHMAN ALRAHEEM '''
    p[0] = "✅ الآية صحيحة"


# Gestion des erreurs syntaxiques
def p_error(p):
    if p:
        raise Exception(f"⛔ خطأ نحوي: الكلمة '{p.value}' في الموضع {p.lexpos} غير صحيحة.")
    raise Exception("⛔ العبارة غير مكتملة أو تحتوي على خطأ!")

# Construire le parser
parser = yacc.yacc()##parser.parse()

# Liste des mots corrects dans la sourate Al-Fatiha
mots_corrects = [##Action sematique verification  
    "بسم", "الله", "الرحمن", "الرحيم", "الحمد", "لله", "رب", "العالمين",
    "الرحمن", "الرحيم", "مالك", "يوم", "الدين", "إياك", "نعبد", "وإياك", "نستعين",
    "اهدنا", "الصراط", "المستقيم", "صراط", "الذين", "أنعمت", "عليهم", "غير",
    "المغضوب", "عليهم", "ولا", "الضالين"
]
# اقتراحات موسعة للكلمات الخاطئة
def generer_suggestions(mot):
    suggestions = get_close_matches(mot, mots_corrects, n=3, cutoff=0.6)
    if suggestions:
        return f"⛔ خطأ في الكلمة '{mot}'. هل كنت تقصد: {', '.join(suggestions)}؟"
    return f"⛔ خطأ في الكلمة '{mot}'. هذه الكلمة غير صحيحة ولا توجد اقتراحات متاحة."

# التحقق من الكلمات المفقودة
def verifier_mots_manquants(mots_entree):
    index_correct = 0
    for mot in mots_corrects:
        if index_correct < len(mots_entree) and mots_entree[index_correct] == mot:
            index_correct += 1
        else:
            return f"⛔ الكلمة '{mot}' متوقعة بعد '{mots_entree[index_correct - 1]}'." if index_correct > 0 else f"⛔ يجب أن تبدأ السورة بـ '{mots_corrects[0]}'."
    return None

# التحقق من التكرار أو الكلمات الزائدة
def verifier_doublons_ou_mots_en_trop(mots_entree):
    mots_verifies = []
    for mot in mots_entree:
        if mot in mots_verifies:
            return f"⛔ الكلمة '{mot}' مكررة بشكل غير ضروري."
        if mot not in mots_corrects:
            return f"⛔ الكلمة '{mot}' زائدة ولا تنتمي إلى السورة."
        mots_verifies.append(mot)
    return None

# التحقق من ترتيب الكلمات
def verifier_ordre(mots_entree):
    sourate_reduite = " ".join(mots_corrects)
    texte_reduit = " ".join(mots_entree)
    if sourate_reduite != texte_reduit:
        return "⛔ الكلمات ليست بالترتيب الصحيح أو هناك أخطاء في العبارة."
    return None

def verifier_mot_par_mot(text):
    for i in range(len(text.split())):  # Utilisation de range() et len()
        mot = text.split()[i]
        if mot not in mots_corrects:
            return False
    return True  # Correction de l'indentation du return

    

# عرض الكلمات الصحيحة المتبقية
def mots_restants(mots_entree):
    index_correct = len(mots_entree)
    return f"ℹ️ الكلمات المتبقية هي: {' '.join(mots_corrects[index_correct:])}"

def est_arabe(texte):
    #  Hna kt verifie ana koula 7aref f text rah kintami majmou3at 7rouf logha l3aribiya code ascci
    return all('\u0600' <= char <= '\u06FF' or char.isspace() for char in texte)

def analyse_lexical(texte):
    try:
        # Analyse lexicale du texte
        lexer.input(texte)
        while True:
            tok = lexer.token()  # Prendre un token
            if not tok:
                break  # Terminer lorsqu'il n'y a plus de tokens

    except Exception as e:
        # Retourner False en cas d'erreur, et afficher un message d'erreur
       
     return """ ⚠️ لديك خطأ لغوي في النص. <br> Erreur lexical ⚠️ """ # Indiquer qu'il y a une erreur dans l'analyse lexicale   

    return "✅ lexicalement النص  لا يحتوي على أخطاء لغوية"+'<br>'  # Retourner True si l'analyse s'est bien passée

# تحليل النص
def analyser_chaine(texte):#### ici ou on commence l'explication  cette anlyse est seulement semantique 
    # تنظيف النص من التشكيل
    texte = re.sub(r'[ًٌٍَُِّْ]', '', texte)
    mots_entree = texte.split()

    erreurs = []

    # التحقق من الكلمات المفقودة
    erreur_manquante = verifier_mots_manquants(mots_entree)
    if erreur_manquante:
        erreurs.append(erreur_manquante)

  
   
    

    # التحقق من الكلمات الخاطئة
    for i, mot in enumerate(mots_entree):
        if mot not in mots_corrects:
            erreurs.append(generer_suggestions(mot))

    # التحقق من ترتيب الكلمات
    erreur_ordre = verifier_ordre(mots_entree)
    if erreur_ordre:
        erreurs.append(erreur_ordre)

    # في حالة وجود أخطاء، عرض الكلمات المتبقية
    if erreurs:
        erreurs.append(mots_restants(mots_entree))
        return "\n".join(erreurs)

    # التحقق إذا كانت جميع الكلمات بالترتيب الصحيح
    try:
        
        result = parser.parse(texte)## il va allez directement ver p_phrase 
        if result:
            return result
    except Exception as e:
        erreurs.append(str(e))

    return "\n".join(erreurs) if erreurs else "✅ السورة صحيحة!"
##verifier les caracteres en francais 
def is_lettrre_francais(mot):
    # Vérifier si le mot contient uniquement des lettres françaises (y compris les lettres accentuées)
    return bool(re.match(r'^[a-zA-ZéèàâêîôûçœÉÈÀÂÊÎÔÛÇŒ]+$', mot))

# Interface web avec Flask
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    texte = ""
    
    if request.method == "POST":
        texte = request.form.get("texte")
  
        if texte in versets_corrects:  # Vérifier si le texte est un verset correct
            result = "✅ الآية صحيحة"
        elif verifier_mot_par_mot(texte):  # Vérifier si le texte est un mot correct
            result = "✅ الكلمة او الكلمات صحيحة وتنتمي إلى كلمات السورة ولكن :::::::::> " +'<br>' + analyser_chaine(texte)
        elif est_arabe(texte):
            result = analyser_chaine(texte)
        else:
            # Si le texte n'est ni un verset ni un mot correct, analyser davantage
            result = analyse_lexical(texte) 
   
        
         
       
    # Interface HTML
    html = """
 <!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> سورة الفاتحة</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 50px;
            background-color: #f4f4f9;
        }

        nav {
            background-color: #333;
            padding: 10px;
        }

        nav ul {
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: space-around;
        }

        nav ul li a {
            color: white;
            text-decoration: none;
        }

        textarea {
            width: 100%;
            height: 150px;
            font-size: 22px;
            direction: rtl;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #ccc;
            box-sizing: border-box;
        }

        button {
            font-size: 20px;
            padding: 15px 30px;
            margin-top: 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #45a049;
        }

        .result {
            margin-top: 20px;
            font-size: 24px;
            color: #333;
            margin-top: 40px;
        }

        #chat-container {
            display: none;
            position: fixed;
            bottom: 10px;
            right: 10px;
            width: 300px;
            height: 400px;
            border: 1px solid #ccc;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }

        #chat-container.active {
            display: block;
            opacity: 1;
        }

        .content {
            display: none;
        }

        .active-content {
            display: block;
        }

        /* Animation styles for the microphone icon */
        .mic-icon {
            font-size: 50px;
            color: #333;
            transition: color 0.3s, transform 0.5s;
        }

        .mic-icon.active {
            color: red;
            transform: scale(1.2);
        }
    </style>
</head>
<body>
    <nav>
        <ul>
            <li><a href="#" onclick="showSection('compilation')">Compilation</a></li>
            <li><a href="#" onclick="showSection('chatbot')">Chatbot</a></li>
        </ul>
    </nav>

    <div id="compilation" class="content active-content">
        <h1>تحقق من سورة الفاتحة</h1>
        <form method="POST">
            <textarea name="texte" placeholder="اكتب النص هنا...">{{ texte }}</textarea><br>
            <button type="submit">تحليل</button>
        </form>

        <!-- Bouton pour démarrer l'enregistrement avec icône -->
        <button id="dictation-btn" onclick="toggleDictation()">
            <span id="mic-icon" class="mic-icon">🎤</span> التحدث
        </button>
        
        <div class="result">{{ result|safe }}</div>
    </div>

    <div id="chatbot" class="content">
        <h1>الدردشة مع البوت</h1>
        <div id="chat-container">
            <div style="padding: 10px; background: #333; color: white; display: flex; justify-content: space-between; align-items: center;">
                <span>Chatbot</span>
                <button onclick="closeChat()" style="background: none; border: none; color: white;">Close</button>
            </div>
        </div>
    </div>

    <script>
        // Variable to store recognition object and recording status
        let recognition;
        let isRecording = false;

        // Fonction pour afficher la section sélectionnée
        function showSection(sectionId) {
            document.querySelectorAll('.content').forEach(function(section) {
                section.classList.remove('active-content');
            });
            document.getElementById(sectionId).classList.add('active-content');
        }

        // Fonction pour démarrer ou arrêter la dictée vocale
        function toggleDictation() {
            if (isRecording) {
                stopDictation(); // Arrêter l'enregistrement si déjà actif
            } else {
                startDictation(); // Démarrer l'enregistrement
            }
        }

        // Fonction pour démarrer la dictée vocale
        function startDictation() {
            if (window.SpeechRecognition || window.webkitSpeechRecognition) {
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'ar-SA'; // Définir la langue arabe saoudienne
                recognition.continuous = true; // Permet la reconnaissance continue
                recognition.start();

                recognition.onresult = function(event) {
                    const transcript = event.results[event.resultIndex][0].transcript;

                    // Supprimer les virgules et mettre à jour la zone de texte en temps réel
                    const filteredTranscript = transcript.replace(/,/g, ''); // Ignorer les virgules
                    document.querySelector('textarea[name="texte"]').value = filteredTranscript;
                }

                recognition.onerror = function(event) {
                    console.error("Error occurred in recognition: " + event.error);
                }

                // Animation de l'icône
                document.getElementById('mic-icon').classList.add('active');
                isRecording = true; // Mise à jour du statut d'enregistrement
            } else {
                alert("Désolé, votre navigateur ne prend pas en charge la reconnaissance vocale.");
            }
        }

        // Fonction pour arrêter la dictée vocale
        function stopDictation() {
            if (recognition) {
                recognition.stop(); // Arrêter la reconnaissance vocale
                document.getElementById('mic-icon').classList.remove('active'); // Arrêter l'animation
                isRecording = false; // Mise à jour du statut d'enregistrement
            }
        }
    </script>
</body>
</html>

    """

    return render_template_string(html, texte=texte, result=result)


if __name__ == "__main__":
    app.run(debug=True)
