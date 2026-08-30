# Kuckuck Werners Berg

Konzept: Ein Erlebniswanderweg um Den Rothenberg für jedermann, mit Stationen die für alle Altersgruppen etwas ansprechendes bieten.

Titel: "Kuckuck Werners Berg"

Untertitel: "Folge Kuckuck Werner und seinen tierischen Freunden um seinen Berg"

# Stationskonzept

Das Wortspiel im Untertitel mit den tierischen Freunden eignet sich, um jede Station in die gleichen drei Elemente aufzugliedern. Das hilft dem Wiedererkennungswert und wirkt auch mehr wie aus einem Guss.
Die Elemente sind stets an die gleichen Zielgruppen gerichtet und erlauben es Besuchern, jenes zu wählen, was am besten zu Ihnen passt.

Es wird daher an jeder Station (repäsentiert durch eine statische Webseite) die gleichen drei Elemente geben: Fuchs (Wissen), Eichhörnchen (Bewegungsspiel) und Kuckuck (Suchspiel).

Die Umsetzung erfolgt mittels QR-Codes - im Wald selbst wird es nur kleine Schilder geben die mittels QR-Codes auf diese Seiten führen.
Dies erlaubt es bei Feedback den Inhalt einfach nachträglich anzupassen ohne im Wald große Anpassungen vornehmen zu müssen.
Weiterhin hält dies den Wald für alle die nicht auf dem Erlebnisweg sind frei von zu vielen Ablenkungen.

## Fuchs: “Schon gewusst?”

Hierbei geht es um Informationen zu umgebenden Objekten oder Themen.
Am Brunnen kann dies die Geschichte des Brunnens sein, an anderer Stelle aber einfach auch zum Beispiel mal etwas zum Waldbau in der Pfalz.
Einfach kleine Wissensbrocken, die den Weg ein wenig unterhaltsamer machen.

## Eichhörnchen: “Schon bewegt?”

Hierbei geht es um kleine Bewegungsübungen, die Jung und Alt durchführen können, um das Wandern ein wenig aufzulockern.

## Kuckuck: "Schon gehört oder gar gefunden?”

Ein Suchspiel in der Umgebung der Station, hierzu erstellen wir für jede Station eine kleine Vogel-Silhouette die wir in der Nähe verstecken und suchen lassen.
Es gibt stets einen Hinweis, wo man suchen sollte. Der Text dieses Hinweises beginnt stets gleich:

  “Habt Ihr den Kuckuck Werner schon gehört?" "Nein, ja leider ist er selten geworden, aber suche doch mal …”

gefolgt von einem Hinweis zum Ort an dieser Station.

Wir erstellen Silhouetten von 18 verschiedenen Vögeln die im Pfälzer Wald vorkommen, gesucht wird aber “Kuckuck Werner”

Wir arbeiteten Landesforsten RLP zusammen und es gibt auch genug öffentliche informationen über Vogelarten zum Beispiel [https://www.wald.rlp.de/wald/voegel](https://www.wald.rlp.de/wald/voegel).
Hiermit werden dann Silhouetten von gut unterscheidbaren Vögeln neu erstellt, diese werden in Konturen umgewandelt und letztendlich als Objekte gefertigt die wir im Wald verstecken können.

Man muss den Vogel aber nicht nur finden, sondern auch erkennen.
Hierzu können die Kinder einfach nur die Silouhetten erkennen aber auch die Form verschiedener Vögel kennen lernen.

Wir bieten auf jeder Seite drei Vögelsilhouetten zum auswählen an, man erhält eine Bestätigung wenn der korrekte identifiziert wurde.

## Technik

* Texte sollen gewissen Einschränkungen unterliegen, damit sie Unterhaltsam bleiben und schnell erfasst werden können
  * Info: maximal zwei durchschnittliche Smartphone Seiten (weiterführende links erlaubt)
  * Bewegungsspiel: maximal eine durchschnittliche Smartphone Seite
  * Suchspiel: der Hinweis wo man suchen sollte und die drei Optionen sollten auf einem durchschnittlichen Smartphone auf einmal angezeigt werden können

## Struktur

* README.md - diese Datei
* /station - Eine Datei je Station welche die Inhalte an dieser Station beschreibt
* /vogel - Ein Vogel für jede der 18 Stationen im format `<nummer>_<name>`
* /logos - Logos für die Sektionen in jeder Station für Eichhörnchen, Fuchs und Kuckuck. Sowie ein kombiniertes logo für den Weg in allgemeinen
* /html - Verzeichnis zum export auf die Webseite, generiert aus den Daten im Repository
* /build - aller Code der, ausser dem Makefile, zur Erstellung der Seiten gebraucht wird
* /misc - Restliche Dateien von der Erstellung als Archive falls nochmals gebraucht

