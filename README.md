# Q1

Le nom de l'algorithme de chiffrement est "XORCipher". Il n'est pas robuste car il est simple et donc facile à comprendre et à exécuter. Il est alors de faible sécurité puisque l'attaquant peut remonter au message avec la simple connaissance de la clé. De plus, cet algorithme répète la clé jusqu'à ce qu'elle ait une longueur égale à la longueur des données.

# Q2

Il n'est pas préférable de hacher le sel et la clé car cela ne donnerait pas plus de sécurité. Hacher le sel et la clé n'apporterait pas plus de hasard puisqu'ils sont déjà associés à des valeurs aléaoires et uniques. Cela n'augmenterait alors pas la difficulté à les deviner.
Un HMAC permettrait de garantir l'intégrité et l'authenticité d'un message. Cela n'est pas essentiel dans ce contexte où la sécurité de la dérivation de clé doit être garanie.

# Q3

Il est préférable de vérifier qu'un fichier token n'est pas présent car cela permet de ne pas écraser les données de chiffrement provenant du passé qui seraient éventuellement présentes. Ne pas faire cette action de vérification pourrait alors entraîner le déchiffrement des données qui avaient déjà été chiffrées auparavant, ce qui peut causer une perte d'informations définitive.

# Q4

Pour vérifier que la clé est bonne, il faut comparer le token obtenu à la suite de la dérivation de la clé et du sel avec le token stocké d'origine.