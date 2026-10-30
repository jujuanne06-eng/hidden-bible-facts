"""Build topic_plan.json: 730 topics (2 a day for one year), mixed across categories.

The first 60 (month 1) are fixed below; the rest are spread evenly so the same
category rarely comes twice in a row. Feast days (SEASONAL) are moved to their date.
Run: python src/build_plan.py
"""
import re
import sys
from datetime import date, timedelta

from common import ROOT, save_json

START = date(2026, 11, 9)
SLOTS = ["08:00", "20:00"]

CATEGORIES = {
    "Old Testament people": (110, """Adam, Eve, Cain, Abel, Seth, Enoch, Methuselah, Noah, Nimrod, Abraham, Sarah,
        Hagar, Ishmael, Lot, Lot's wife, Melchizedek, Isaac, Rebekah, Esau, Jacob, Rachel, Leah, Laban, Joseph,
        Judah, Benjamin, Reuben, Dinah, Tamar, Potiphar, Moses, Aaron, Miriam, Jethro, Zipporah,
        the Pharaoh of the Exodus, Joshua, Caleb, Rahab, Balaam, Korah, Deborah, Jael, Gideon, Samson, Delilah,
        Jephthah, Ehud, Ruth, Naomi, Boaz, Hannah, Samuel, Eli, King Saul, Jonathan, King David, Goliath,
        Bathsheba, Uriah the Hittite, the prophet Nathan, Absalom, Michal, Abigail, King Solomon,
        the Queen of Sheba, Rehoboam, Jeroboam, King Ahab, Jezebel, Elijah, Elisha, Naaman, Jonah, Daniel,
        Nebuchadnezzar, Belshazzar, Cyrus the Great, Esther, Mordecai, Haman, Ezra, Nehemiah, Job, King Hezekiah,
        King Josiah, King Manasseh, King Jehu, Queen Athaliah, Huldah the prophetess, Joab, Abner, Mephibosheth,
        Lamech, Og of Bashan, Phinehas, Achan, Shadrach Meshach and Abednego, Sennacherib, Darius the Mede,
        Tubal-cain, Barak, Ham the son of Noah, Zerubbabel, Gomer, Baruch the scribe,
        Obed the grandfather of David, Asenath, Shem, Jochebed"""),
    "New Testament people": (70, """Jesus, Mary the mother of Jesus, Joseph of Nazareth, John the Baptist,
        Elizabeth, Zechariah the priest, Peter, Andrew, James son of Zebedee, John the Apostle, Philip the Apostle,
        Bartholomew, Matthew the tax collector, Thomas, James son of Alphaeus, Thaddeus, Simon the Zealot,
        Judas Iscariot, Matthias, the Apostle Paul, Barnabas, Silas, Timothy, Luke the physician, Mary Magdalene,
        Martha, Lazarus, Nicodemus, Joseph of Arimathea, Zacchaeus, Pontius Pilate, Herod the Great, Herod Antipas,
        Herodias, Salome, Caiaphas, Barabbas, Simon of Cyrene, the three wise men, Stephen, Philip the Evangelist,
        the Ethiopian eunuch, Cornelius the centurion, Lydia of Thyatira, Priscilla and Aquila, Apollos, Onesimus,
        Gamaliel, Ananias of Damascus, Ananias and Sapphira, Dorcas, Eutychus, Simon Magus, Governor Felix,
        Herod Agrippa, Anna the prophetess, Simeon of Jerusalem, Jairus, Bartimaeus, Malchus, Mary of Bethany,
        Joanna, Jude the brother of Jesus, the thief on the cross, James the brother of Jesus,
        the Samaritan woman, the shepherds of Bethlehem, John Mark, Phoebe, the centurion at the cross"""),
    "Bible stories": (90, """the creation story, the Garden of Eden, the forbidden fruit, the Great Flood,
        Noah's Ark, the Tower of Babel, Sodom and Gomorrah, the binding of Isaac, Jacob's ladder,
        Joseph's coat of many colors, the burning bush, the ten plagues of Egypt, the first Passover,
        the parting of the Red Sea, manna from heaven, the Ten Commandments, the golden calf, the walls of Jericho,
        the day the sun stood still, David and Goliath, Daniel in the lions' den, the fiery furnace,
        the writing on the wall, Jonah and the whale, Elijah and the prophets of Baal, the chariot of fire,
        the Babylonian exile, the Nativity, the star of Bethlehem, the flight into Egypt, the baptism of Jesus,
        the temptation in the desert, the wedding at Cana, the Sermon on the Mount,
        the feeding of the five thousand, Jesus walking on water, the Transfiguration, the raising of Lazarus,
        the parable of the Prodigal Son, the parable of the Good Samaritan, the parable of the talents,
        the Last Supper, the Garden of Gethsemane, the betrayal of Jesus, Peter's denial, the trial of Jesus,
        the crucifixion, the empty tomb, the road to Emmaus, doubting Thomas, the Ascension, Pentecost,
        the conversion of Paul, Paul's shipwreck, Paul's missionary journeys, the stoning of Stephen,
        the Council of Jerusalem, the Four Horsemen, the number of the beast, Armageddon, the New Jerusalem,
        the Beatitudes, the Lord's Prayer, the Golden Rule, the cleansing of the Temple, the entry into Jerusalem,
        the healing of the blind man, the calming of the storm, the miraculous catch of fish,
        the parable of the lost sheep, the parable of the mustard seed, the parable of the ten virgins,
        Jesus washing the disciples' feet, the Exodus, forty years in the desert, the twelve spies of Canaan,
        Balaam's talking donkey, the Witch of Endor, the judgment of Solomon, Elisha and the bears,
        the massacre of the innocents, Jesus lost in the Temple, the healing of the ten lepers,
        the Great Commission, the rich young man, the widow's offering, the fall of Satan, the seven seals,
        the Annunciation, the resurrection of Jesus"""),
    "Books of the Bible": (54, """the Book of Genesis, the Book of Exodus, the Book of Leviticus, the Book of Numbers,
        the Book of Deuteronomy, the Book of Judges, the Books of Samuel, the Books of Kings,
        the Books of Chronicles, the Book of Psalms, the Book of Proverbs, the Book of Ecclesiastes,
        the Song of Songs, the Book of Lamentations, the Book of Isaiah, the Book of Jeremiah, the Book of Ezekiel,
        the Book of Hosea, the Book of Amos, the Book of Micah, the Book of Habakkuk, the Book of Zechariah,
        the Book of Malachi, the Book of Joel, the Book of Nahum, the Book of Zephaniah, the Book of Haggai,
        the Book of Obadiah, the Gospel of Matthew, the Gospel of Mark, the Gospel of Luke, the Gospel of John,
        the Book of Acts, the Letter to the Romans, the First Letter to the Corinthians,
        the Second Letter to the Corinthians, the Letter to the Galatians, the Letter to the Ephesians,
        the Letter to the Philippians, the Letter to the Colossians, the Letters to the Thessalonians,
        the Letters to Timothy, the Letter to Titus, the Letter to Philemon, the Letter to the Hebrews,
        the Letter of James, the Letters of Peter, the Letters of John, the Letter of Jude, the Book of Revelation,
        the Book of Enoch, the Gospel of Thomas, the Books of Maccabees, the Book of Tobit"""),
    "Bible places": (60, """Jerusalem, Bethlehem, Nazareth, the Sea of Galilee, the Jordan River, the Dead Sea,
        Mount Sinai, Mount Ararat, Babylon, Nineveh, Jericho, Capernaum, Bethany, Golgotha, the Mount of Olives,
        Solomon's Temple, the Western Wall, Masada, Qumran, Damascus, Antioch, Ephesus, Corinth, the Areopagus,
        the island of Patmos, Tarsus, Ur of the Chaldees, Hebron, Beersheba, Shiloh, Bethel, Samaria, Megiddo,
        Mount Carmel, Mount Tabor, Mount Hermon, the Judean desert, the Negev, Petra, Tyre and Sidon,
        the land of Canaan, the land of Goshen, Moab, Edom, the pool of Siloam, the pool of Bethesda,
        Caesarea Maritima, Caesarea Philippi, Mount Nebo, Mount Moriah, the Via Dolorosa, the Upper Room,
        Hezekiah's tunnel, the City of David, Susa, Thessalonica, Philippi, the seven churches of Revelation,
        Laodicea, the cedars of Lebanon"""),
    "Saints": (90, """Saint Patrick, Saint Nicholas, Saint Francis of Assisi, Saint Augustine, Saint Benedict,
        Saint Valentine, Saint George, Saint Christopher, Joan of Arc, Saint Thomas Aquinas, Saint Teresa of Avila,
        Mother Teresa, Saint Anthony of Padua, Saint Anthony the Great, Saint Jerome, Saint Ambrose,
        Saint Catherine of Siena, Saint Clare of Assisi, Saint Ignatius of Loyola, Saint Francis Xavier,
        Saint Therese of Lisieux, Saint Bernadette, Padre Pio, Pope John Paul the Second, Saint Monica, Saint Lucy,
        Saint Agnes, Saint Cecilia, Saint Sebastian, Saint Lawrence, Saint Polycarp, Saint Ignatius of Antioch,
        Saint Perpetua, Saint Athanasius, Saint Basil the Great, Pope Gregory the Great, Saint John Chrysostom,
        Saints Cyril and Methodius, Saint Boniface, Saint Columba, Saint Brigid, Saint David of Wales,
        Saint Simeon Stylites, Saint Mary of Egypt, Saint Kateri Tekakwitha, Saint Rose of Lima,
        Saint Martin de Porres, Saint Juan Diego, Saint Vincent de Paul, Saint Dominic, Saint Bernard of Clairvaux,
        Hildegard of Bingen, Saint Thomas Becket, Saint Thomas More, Saint Elizabeth of Hungary,
        Saint Wenceslaus, Saint Olaf, Saint Louis of France, Saint Bede, Saint Cuthbert, Saint Joseph of Cupertino,
        Saint Maximilian Kolbe, Saint Edith Stein, Saint Faustina, Saint John of the Cross, Saint Philip Neri,
        Saint Francis de Sales, Saint John Bosco, Saint Isidore of Seville, Saint Blaise, Saint Denis,
        Saint Genevieve, Saint Martin of Tours, Saint Helena, Saint Scholastica, Saint Anne, Saint Barbara,
        Saint Roch, Saint Josephine Bakhita, Saint Oscar Romero, Saint Damien of Molokai, Saint Frances Cabrini,
        Saint Moses the Black, Saint Seraphim of Sarov, Saint Sergius of Radonezh, Saint Nino of Georgia,
        Saint Gregory the Illuminator, Saint Hubert, Saint Stanislaus, Saint Ansgar"""),
    "Church history": (80, """the first Christians, the catacombs of Rome, the persecution under Nero,
        Constantine the Great, the Edict of Milan, the Council of Nicaea, the Nicene Creed, the Desert Fathers,
        the first monks, the Great Schism, the Crusades, the First Crusade, the Children's Crusade,
        the Knights Hospitaller, the Knights Templar, the Inquisition, the Spanish Inquisition, the Avignon popes,
        the Western Schism, Martin Luther, the Ninety-Five Theses, the Protestant Reformation, John Calvin,
        Henry the Eighth and the Church, the Church of England, the Council of Trent, the Jesuits,
        William Tyndale, John Wycliffe, Jan Hus, the Gutenberg Bible, the King James Bible, the Pilgrims,
        the Puritans, the Quakers, the Amish, the Mennonites, John Wesley, the Methodists, the Baptists,
        the Great Awakening, the Salvation Army, William Wilberforce, Dietrich Bonhoeffer, C. S. Lewis,
        Billy Graham, the Dead Sea Scrolls, the Codex Sinaiticus, relics, the Vatican, the Swiss Guard,
        the papal conclave, the first pope, the Coptic Church, the Ethiopian Church, Armenia the first Christian nation,
        the Orthodox Church, the Church of the East, the Saint Thomas Christians of India,
        the hidden Christians of Japan, Christian missionaries, the Franciscans, the Benedictines, the Cistercians,
        the Carmelites, medieval monasteries, illuminated manuscripts, the Book of Kells, Gregorian chant,
        Johann Sebastian Bach, Handel's Messiah, the hymn Amazing Grace, the Huguenots, Thomas Cranmer, Erasmus,
        Blaise Pascal, Gregor Mendel, Georges Lemaitre, pilgrimages, the Celtic Church"""),
    "Churches and cathedrals": (60, """Notre-Dame de Paris, Saint Peter's Basilica, the Sistine Chapel, Hagia Sophia,
        the Sagrada Familia, Westminster Abbey, Canterbury Cathedral, Cologne Cathedral, Chartres Cathedral,
        Milan Cathedral, Saint Paul's Cathedral, the Church of the Holy Sepulchre, the Church of the Nativity,
        Mont-Saint-Michel, Saint Basil's Cathedral, Florence Cathedral, the rock churches of Lalibela,
        Hallgrimskirkja, Las Lajas Sanctuary, Washington National Cathedral, Saint Patrick's Cathedral in New York,
        the Basilica of Guadalupe, Christ the Redeemer, Lourdes, Fatima, the Meteora monasteries, Mount Athos,
        Saint Catherine's Monastery, the Sedlec Ossuary, the Capuchin Crypt, Salisbury Cathedral, York Minster,
        Durham Cathedral, Reims Cathedral, Seville Cathedral, Santiago de Compostela, Siena Cathedral,
        Saint Mark's Basilica, the Pantheon in Rome, Sainte-Chapelle, the Cathedral of Brasilia, Ulm Minster,
        Aachen Cathedral, the Rila Monastery, Etchmiadzin Cathedral, the Basilica of Our Lady of Peace,
        the Cathedral of Christ the Saviour, the Kizhi churches, the California missions, Saint Vitus Cathedral,
        the Salt Cathedral of Zipaquira, the Rock Church of Helsinki, Norway's stave churches,
        the Basilica of Saint John Lateran, the Painted Monasteries of Romania, the Abbey of Cluny,
        Lindisfarne, Iona Abbey, Glendalough, the Cathedral of Light in Oakland"""),
    "Traditions and holidays": (50, """Christmas, Easter, Lent, Ash Wednesday, Good Friday, Palm Sunday, Holy Week,
        Advent, the Advent wreath, Epiphany, Christmas trees, nativity scenes, Christmas carols, Easter eggs,
        hot cross buns, Mardi Gras, All Saints' Day, All Souls' Day, Halloween, baptism, Holy Communion,
        confession, confirmation, the rosary, the sign of the cross, Christian weddings, church bells,
        candles in church, incense, holy water, Sunday, hymns, gospel music, Christian fasting,
        the twelve days of Christmas, Candlemas, Corpus Christi, Orthodox Easter, the Stations of the Cross,
        monastic life, nuns, church organs, midnight Mass, the Feast of the Assumption, Reformation Day,
        saying grace, the Sabbath, Christian names, the Easter Vigil, Pancake Day"""),
    "Symbols and mysteries": (42, """the cross, the crucifix, the ichthys fish symbol, the Chi Rho, the dove,
        the Lamb of God, the halo, the Ark of the Covenant, the Holy Grail, the Shroud of Turin, the True Cross,
        stained glass windows, Orthodox icons, frankincense and myrrh, the crown of thorns, Alpha and Omega,
        gargoyles, the bishop's crozier, the Urim and Thummim, the bronze serpent, the Tabernacle,
        the Temple veil, the anchor symbol, the keys of heaven, the sign above the cross,
        the thirty pieces of silver, the staff of Moses, the menorah, unicorns in the Bible, the Leviathan,
        the Behemoth, the Nephilim, angels, cherubim, seraphim, the archangel Michael, the angel Gabriel,
        Lucifer, the serpent of Eden, locusts in the Bible, sheep and shepherds, the seven deadly sins"""),
    "Words and translations": (24, """the word Bible, the word Amen, Hallelujah, the word Christ, the name Jesus,
        biblical Hebrew, Aramaic, Koine Greek, the Septuagint, the Latin Vulgate, Bible chapters and verses,
        the shortest verse in the Bible, the most translated book, the word Gospel, the word Messiah,
        the word Apostle, Hosanna, the word Easter, the word Christmas, everyday phrases from the Bible,
        the name of God, the word Abba, the word Selah, the word Satan"""),
}

MONTH_1 = """Noah's Ark, the Dead Sea Scrolls, Moses, Notre-Dame de Paris, the Garden of Eden, the Knights Templar,
    Jerusalem, King David, the Shroud of Turin, Judas Iscariot, the Sistine Chapel, the Book of Revelation,
    the Great Flood, Mary Magdalene, unicorns in the Bible, Bethlehem, Samson, the Ark of the Covenant,
    the parting of the Red Sea, Saint Augustine, the Tower of Babel, Hagia Sophia, the Apostle Paul, the Nephilim,
    Jonah and the whale, Pontius Pilate, the catacombs of Rome, King Solomon, Methuselah, the Sea of Galilee,
    Joan of Arc, the Book of Enoch, Elijah, the Holy Grail, Peter, the walls of Jericho, the Sagrada Familia,
    Goliath, the angel Gabriel, Daniel, the King James Bible, Mount Sinai, Sodom and Gomorrah,
    the Queen of Sheba, the Vatican, John the Baptist, the Leviathan, the word Amen, Esther, the Swiss Guard,
    Nazareth, Jezebel, the Annunciation, Mount Ararat, the archangel Michael, Lazarus, the creation story,
    Saint Christopher, Golgotha, the Book of Genesis"""

# feast-day topics moved to their date (movable feasts use the 2027 dates: Easter is 28 March 2027)
SEASONAL = {
    "advent": "2026-11-29", "the-advent-wreath": "2026-11-30", "saint-nicholas": "2026-12-06",
    "saint-lucy": "2026-12-13", "christmas-trees": "2026-12-19", "nativity-scenes": "2026-12-20",
    "the-word-christmas": "2026-12-21", "christmas-carols": "2026-12-22", "the-nativity": "2026-12-23",
    "the-star-of-bethlehem": "2026-12-24", "midnight-mass": "2026-12-24", "christmas": "2026-12-25",
    "the-twelve-days-of-christmas": "2026-12-26", "the-three-wise-men": "2027-01-05", "epiphany": "2027-01-06",
    "candlemas": "2027-02-02", "mardi-gras": "2027-02-08", "pancake-day": "2027-02-09",
    "ash-wednesday": "2027-02-10", "lent": "2027-02-11", "saint-valentine": "2027-02-14",
    "saint-patrick": "2027-03-17", "the-entry-into-jerusalem": "2027-03-20", "palm-sunday": "2027-03-21",
    "holy-week": "2027-03-22", "the-stations-of-the-cross": "2027-03-23", "the-word-easter": "2027-03-24",
    "the-last-supper": "2027-03-25", "hot-cross-buns": "2027-03-25", "good-friday": "2027-03-26",
    "the-crucifixion": "2027-03-26", "the-easter-vigil": "2027-03-27", "easter-eggs": "2027-03-27",
    "easter": "2027-03-28", "the-resurrection-of-jesus": "2027-03-28", "the-empty-tomb": "2027-03-29",
    "saint-george": "2027-04-23", "orthodox-easter": "2027-05-02", "the-ascension": "2027-05-06",
    "pentecost": "2027-05-16", "corpus-christi": "2027-05-27", "the-feast-of-the-assumption": "2027-08-15",
    "saint-francis-of-assisi": "2027-10-04", "halloween": "2027-10-31", "reformation-day": "2027-10-31",
    "all-saints-day": "2027-11-01", "all-souls-day": "2027-11-02",
}


def split(text):
    return [t.strip() for t in text.replace("\n", " ").split(",") if t.strip()]


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def main():
    category_of, problems = {}, []
    for category, (target, text) in CATEGORIES.items():
        titles = split(text)
        if len(titles) != target:
            problems.append(f"{category}: {len(titles)} topics, expected {target}")
        for title in titles:
            if slug(title) in category_of:
                problems.append(f"duplicate: {title}")
            category_of[slug(title)] = (category, title)
    if len(category_of) != 730:
        problems.append(f"{len(category_of)} topics in total, expected 730")

    month_1 = [slug(t) for t in split(MONTH_1)]
    problems += [f"month 1 topic not in a category: {s}" for s in month_1 if s not in category_of]
    problems += [f"month 1 topic has a feast day: {s}" for s in month_1 if s in SEASONAL]
    problems += [f"seasonal topic not in a category: {s}" for s in SEASONAL if s not in category_of]
    if len(set(month_1)) != 60:
        problems.append(f"month 1 has {len(set(month_1))} different topics, expected 60")
    if problems:
        sys.exit("\n".join(problems))

    # spread the rest evenly: item k of a category with n items sits at position (k + 0.5) / n
    rest = []
    for category, (_, text) in CATEGORIES.items():
        items = [slug(t) for t in split(text) if slug(t) not in month_1 and slug(t) not in SEASONAL]
        rest += [((k + 0.5) / len(items), category, s) for k, s in enumerate(items)]
    order = month_1 + [s for _, _, s in sorted(rest)]

    # then each feast-day topic goes in the morning slot of its date (evening if the morning is taken)
    wanted = {}
    for s, day in SEASONAL.items():
        i = (date.fromisoformat(day) - START).days * 2
        while i in wanted:
            i += 1
        wanted[i] = s
    for i in sorted(wanted):
        order.insert(i, wanted[i])

    plan = []
    for i, s in enumerate(order):
        category, title = category_of[s]
        plan.append({"n": i + 1, "date": str(START + timedelta(days=i // 2)), "time": SLOTS[i % 2],
                     "id": s, "category": category, "title": title})
    save_json(ROOT / "topic_plan.json", plan)
    print(f"{len(plan)} topics, {plan[0]['date']} -> {plan[-1]['date']}")


if __name__ == "__main__":
    main()
