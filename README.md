Documentation de la Solution Factur-X Architect

Cette solution est composée de deux pages principales et s'appuie sur une structure de fichiers JSON pour une personnalisation dynamique sans code.

1. Les Pages du Site

index.html (Tableau de bord) :
C'est la porte d'entrée. Elle offre une vue d'ensemble et permet de naviguer vers les outils de génération ou de validation (en cours de développement). Design moderne en mode sombre avec effets de verre ("Glassmorphism").

genere-factur-x.html (Générateur) :
L'outil principal. Il permet de saisir les informations de facturation, de calculer les totaux en temps réel et de générer un PDF au standard Factur-X (incluant le XML de données).

2. Fichiers de Configuration (JSON)
L'outil est conçu pour être "Data-Driven". Modifiez ces fichiers pour changer le comportement par défaut :

seller.json (Votre Profil Émetteur) :
Contient vos informations légales (Nom, SIRET, TVA, Adresse).
Nouveau : Inclut les champs conditions (texte libre pour les notes), iban (coordonnées bancaires), site et email pour le pied de page du PDF.

buyers.json (Base Clients) :
Une liste d'objets clients. En sélectionnant un client dans le menu déroulant, tous ses champs (Adresse, Email, SIRET) se remplissent automatiquement.

items.json (Lignes par défaut) :
Permet de définir les prestations ou produits qui apparaissent dès l'ouverture de la page. Si ce fichier est vide ou absent, l'outil démarre sur une ligne vierge.

3. Gestion du Logo
Fichier : images/logobyosphere.png
Usage :
Interface : S'affiche en haut à droite du bloc "Émetteur".
PDF : S'insère automatiquement en haut à gauche, à côté du nom de votre entreprise.
Note : L'image doit être au format PNG avec un fond transparent de préférence.

4. Fonctionnalités de Sécurité et UI
Validation intelligente : Le bouton "Générer la facture" reste bloqué (semi-transparent) tant que vous n'avez pas sélectionné un client ou si le contenu de la facture est vide.
Alignement Automatique : Les colonnes de calculs (Prix, Quantité, TVA) sont alignées au centre dans l'interface et le PDF pour une lecture professionnelle.
Calculs Temps Réel : Tous les totaux (HT, TVA par taux, TTC) sont recalculés à chaque modification de valeur ou de quantité.

5. Versions déployées
* 16/04/2026 : Site permettant de générer des factures au format Factur-X, mais aussi de valider des factures au format Factur-X. Norme Couche PDF : Format PDF/A-3. Norme Couche XML : format UN/CEFACT CII.
* 16/04/2026 : version 1.0 gestion des clients et des factures au format Factur-X, validation des factures au format Factur-X
