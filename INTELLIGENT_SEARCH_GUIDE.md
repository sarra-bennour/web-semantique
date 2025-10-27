# 🔍 Guide du Système de Recherche Intelligent

## Vue d'ensemble

Le système de recherche sémantique a été amélioré avec une logique intelligente qui peut interpréter et répondre à des questions complexes sur les volontaires et les assignements en langage naturel.

## 🎯 Fonctionnalités Principales

### 1. **Reconnaissance Intelligente des Questions**
- Détection automatique des mots-clés dans les questions
- Patterns de reconnaissance pour différents types de requêtes
- Gestion des variations linguistiques (actif/active, volontaire/bénévole, etc.)

### 2. **Questions sur les Volontaires**

#### **Niveaux d'Activité**
- `"qui sont les volontaires non actifs"` → Volontaires inactifs
- `"quels volontaires sont très actifs"` → Volontaires très actifs
- `"quels volontaires sont actifs"` → Volontaires actifs

#### **Compétences**
- `"quelles sont les compétences des volontaires"` → Tous les volontaires avec compétences
- `"quels volontaires ont des compétences en programmation"` → Volontaires avec compétences spécifiques

#### **Expérience**
- `"quels volontaires ont de l'expérience"` → Volontaires expérimentés
- `"quels volontaires sont expérimentés"` → Volontaires expérimentés

#### **Conditions Médicales**
- `"quels volontaires n'ont pas de conditions médicales"` → Volontaires sans restrictions
- `"quels volontaires ont des conditions médicales"` → Volontaires avec conditions

#### **Motivation**
- `"quels volontaires sont motivés"` → Volontaires avec motivation
- `"quels volontaires ont une motivation"` → Volontaires motivés

#### **Contacts**
- `"quels sont les contacts des volontaires"` → Volontaires avec informations de contact

#### **Statistiques**
- `"combien y a-t-il de volontaires"` → Nombre total de volontaires
- `"statistiques des volontaires"` → Statistiques détaillées

### 3. **Questions sur les Assignements**

#### **Statuts**
- `"quels assignements sont approuvés"` → Assignements approuvés
- `"quels assignements sont rejetés"` → Assignements rejetés
- `"quels assignements sont non approuvés"` → Assignements non approuvés

#### **Notes/Évaluations**
- `"quelles sont les notes des assignements"` → Assignements avec notes
- `"quels assignements ont une note de 5 étoiles"` → Assignements 5 étoiles
- `"quels assignements ont une note de 4 étoiles et plus"` → Assignements bien notés

#### **Dates**
- `"quels assignements sont récents"` → Assignements récents
- `"quels assignements sont nouveaux"` → Nouveaux assignements

#### **Relations**
- `"assignements par volontaire"` → Assignements groupés par volontaire
- `"assignements par événement"` → Assignements groupés par événement

#### **Statistiques**
- `"combien y a-t-il d'assignements"` → Nombre total d'assignements
- `"statistiques des assignements"` → Statistiques détaillées

## 🔧 Architecture Technique

### **Fonctions Principales**

1. **`handle_volunteer_questions(question_lower)`**
   - Gère toutes les questions sur les volontaires
   - Patterns de reconnaissance intelligents
   - Génération de requêtes SPARQL optimisées

2. **`handle_assignment_questions(question_lower)`**
   - Gère toutes les questions sur les assignements
   - Patterns de reconnaissance intelligents
   - Génération de requêtes SPARQL optimisées

### **Priorité de Traitement**

1. **Volontaires** - Priorité absolue
2. **Assignements** - Priorité absolue
3. **Autres entités** - Traitement normal

## 📝 Exemples d'Utilisation

### **Questions Simples**
```
"qui sont les volontaires non actifs"
→ Retourne les volontaires avec niveau d'activité "non actif", "inactif", "peu actif"
```

### **Questions Complexes**
```
"quels volontaires ont des compétences en programmation"
→ Retourne les volontaires avec des compétences contenant "programmation"
```

### **Questions de Statistiques**
```
"combien y a-t-il de volontaires"
→ Retourne le nombre total de volontaires avec répartition par catégories
```

## 🚀 Avantages

1. **Flexibilité** - Comprend les variations linguistiques
2. **Intelligence** - Reconnaissance contextuelle des mots-clés
3. **Performance** - Requêtes SPARQL optimisées
4. **Extensibilité** - Facile d'ajouter de nouveaux patterns
5. **Maintenance** - Code modulaire et bien structuré

## 🔄 Processus de Traitement

1. **Analyse** - Détection des mots-clés dans la question
2. **Classification** - Identification du type de question (volontaire/assignement)
3. **Pattern Matching** - Reconnaissance du pattern spécifique
4. **Génération** - Création de la requête SPARQL appropriée
5. **Exécution** - Retour des résultats formatés

## 📊 Patterns Supportés

### **Volontaires**
- Niveaux d'activité (actif, très actif, non actif, inactif)
- Compétences (générales et spécifiques)
- Expérience (expérimenté, ancien, vétéran)
- Conditions médicales (avec/sans)
- Motivation (motivé, intérêt, passion)
- Contacts (téléphone, email)
- Statistiques (nombre, répartition)

### **Assignements**
- Statuts (approuvé, rejeté, non approuvé)
- Notes (1-5 étoiles, plages)
- Dates (récent, nouveau, dernier)
- Relations (volontaire, événement)
- Statistiques (nombre, moyennes)

## 🎯 Résultat

Le système peut maintenant répondre intelligemment à des questions comme :
- "qui sont les volontaires non actifs" ✅
- "quels assignements ont une note de 5 étoiles" ✅
- "combien y a-t-il de volontaires expérimentés" ✅
- "statistiques des assignements approuvés" ✅

Et bien d'autres variations linguistiques et questions complexes !
