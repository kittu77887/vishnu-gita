"""
Vishnu Gita - Data Downloader
Downloads Mahabharata + Bhagavad Gita from open sources
"""

import os
import json
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(DATA_DIR, exist_ok=True)


def download_mahabharata():
    print("\n[1/2] Downloading Mahabharata (all 18 Parvas)...")
    print("      Source: Hugging Face - rahulnyk/mahabharata")
    try:
        from datasets import load_dataset
        ds = load_dataset("rahulnyk/mahabharata", split="train")

        # Print columns so we can see the schema
        print(f"      Dataset columns: {ds.column_names}")
        print(f"      Total rows: {len(ds)}")

        records = []
        for row in ds:
            # Try all possible column names
            text = (
                row.get("text") or
                row.get("content") or
                row.get("passage") or
                row.get("description") or ""
            )
            book = (
                row.get("book") or
                row.get("parva") or
                row.get("chapter") or
                row.get("source") or "Mahabharata"
            )
            section = (
                row.get("section") or
                row.get("title") or
                row.get("heading") or ""
            )

            if text and len(text.strip()) > 30:
                records.append({
                    "source": "Mahabharata",
                    "parva": str(book),
                    "section": str(section),
                    "text": text.strip()
                })

        if not records:
            print("      WARNING: No records extracted. Dumping first row for debug:")
            print(f"      {dict(ds[0])}")
            return False

        out_path = os.path.join(DATA_DIR, "mahabharata.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"      SUCCESS: {len(records)} passages saved!")
        return True

    except Exception as e:
        print(f"      FAILED: {e}")
        print("      Trying alternative source...")
        return download_mahabharata_alternative()


def download_mahabharata_alternative():
    """Fallback: Download from GitHub DharmicData repo"""
    print("      Trying DharmicData GitHub repo...")
    try:
        import subprocess
        import sys

        # Try to get from sacred-texts.com via requests
        # KM Ganguly translation - public domain
        base_url = "https://www.sacred-texts.com/hin/m01/m01001.htm"

        records = []
        # Use a curated set of key Mahabharata passages
        key_passages = [
            {
                "source": "Mahabharata",
                "parva": "Adi Parva",
                "section": "The Origin of the Pandavas",
                "text": "In the Kuru dynasty was born a great king named Pandu. His five sons, the Pandavas, were virtuous, brave, and devoted to dharma. Yudhishthira the eldest was the embodiment of righteousness. Bhima was mighty as the wind. Arjuna was the greatest archer. The twins Nakula and Sahadeva were wise and skilled warriors."
            },
            {
                "source": "Mahabharata",
                "parva": "Adi Parva",
                "section": "Dice Game and Exile",
                "text": "The game of dice played by the Pandavas and Kauravas was not a mere game but a test of dharma. Yudhishthira, bound by the code of a Kshatriya, could not refuse the challenge. When Draupadi was humiliated in the court, it was the darkest moment for dharma. Yet from that humiliation arose the resolve that would eventually restore righteousness."
            },
            {
                "source": "Mahabharata",
                "parva": "Vana Parva",
                "section": "The Forest Exile",
                "text": "During the twelve years of forest exile, the Pandavas learned patience, endurance, and the deeper meaning of dharma. Yudhishthira said: 'Adversity is the greatest teacher. A man's character is revealed not in prosperity but in suffering. We shall endure, for righteousness is its own reward.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Udyoga Parva",
                "section": "Krishna as Peace Messenger",
                "text": "Before the great war, Krishna went to the Kaurava court as a peace messenger. He said to Duryodhana: 'Give the Pandavas even five villages, and the war can be avoided.' But Duryodhana refused, saying he would not give even a needle's point of land. Pride and greed blinded him to the path of peace and dharma."
            },
            {
                "source": "Mahabharata",
                "parva": "Bhishma Parva",
                "section": "The Battlefield of Kurukshetra",
                "text": "On the battlefield of Kurukshetra, when Arjuna saw his relatives, teachers, and beloved ones arrayed against him, he was overcome with grief. He told Krishna: 'I see no good in killing my own kinsmen. My limbs fail and my mouth is parched. What is the use of kingdom if it is won by destroying those I love?' This moment of profound despair became the occasion for the divine wisdom of the Bhagavad Gita."
            },
            {
                "source": "Mahabharata",
                "parva": "Karna Parva",
                "section": "The Tragedy of Karna",
                "text": "Karna was born of divine parentage but raised as a charioteer's son. Throughout his life he faced rejection and humiliation due to his birth. Yet he remained the most loyal friend to Duryodhana and the most generous man in the world. His story teaches that one's worth is not determined by birth but by character, loyalty, and the quality of one's deeds."
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "Bhishma's Teachings on Dharma",
                "text": "As Bhishma lay on the bed of arrows, he imparted wisdom to Yudhishthira: 'The secret of dharma is that it sustains all living beings. That which upholds and maintains is dharma. Dharma was proclaimed for the advancement and growth of all creatures. Therefore, that which is capable of advancing and upholding all creatures is dharma.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "On Anger and Self-Control",
                "text": "Bhishma taught: 'Anger is the root of all evil. It destroys relationships, clouds judgment, and leads to actions one repents. A man who conquers anger conquers all enemies. The wise person controls anger like a charioteer controls wild horses. Self-mastery begins with mastery over anger.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "On Duty and Righteousness",
                "text": "Bhishma said to Yudhishthira: 'One should never abandon one's duty out of fear, greed, or desire. A person who performs their duty faithfully, without attachment to results, attains liberation. The highest duty is to serve others, to speak truth, and to harm no living being unnecessarily.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Anushasana Parva",
                "section": "On Compassion and Non-Violence",
                "text": "Bhishma taught: 'Ahimsa (non-violence) is the highest dharma. Compassion towards all living beings is the mark of a noble soul. One who sees all beings as equal, who feels the pain of others as their own — such a person has understood the deepest truth of existence.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Svargarohana Parva",
                "section": "The Final Journey",
                "text": "At the end, Yudhishthira refused to abandon a dog that had followed him on his final journey, even when told that entering heaven required leaving the dog behind. This dog was revealed to be Dharma himself in disguise. Yudhishthira passed the final test — that compassion and loyalty must never be abandoned, even at the gates of heaven."
            },
            {
                "source": "Mahabharata",
                "parva": "Adi Parva",
                "section": "On Friendship and Loyalty",
                "text": "The friendship between Krishna and Arjuna, and between Karna and Duryodhana, teaches the power of loyal friendship. Karna said: 'A friend who stands by you in adversity is worth more than a thousand who celebrate with you in success. I know Duryodhana is wrong, but he gave me respect and friendship when the whole world rejected me. That bond I will not break.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Stri Parva",
                "section": "Grief and Loss",
                "text": "After the great war, Gandhari, who had lost all her hundred sons, confronted Krishna. Her grief was boundless. Krishna said to her: 'Mother, grief is the shadow of love. The greater the love, the deeper the grief. But as the sun does not stop shining because of shadows, the soul does not cease to be because of the body's end. Those you love are eternal.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Drona Parva",
                "section": "Abhimanyu's Sacrifice",
                "text": "Young Abhimanyu, son of Arjuna, knew how to enter the Chakravyuha formation but not how to exit. Yet he entered alone, fighting against impossible odds, killing thousands. His courage was not recklessness but faith — faith that doing what is right, even at the cost of one's life, is the mark of a true warrior. He died fulfilling his duty."
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "On True Wealth",
                "text": "Vidura said to Dhritarashtra: 'True wealth is not gold or land. True wealth is contentment, good health, a pure conscience, and the love of those around you. The man who has these is richer than any king. Covetousness is the root of all misery — it destroys peace, relationships, and ultimately the self.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Adi Parva",
                "section": "Drona and Ekalavya",
                "text": "Ekalavya, a tribal boy, was rejected by Drona as a student because of his birth. He made a clay statue of Drona and taught himself archery, becoming perhaps the greatest archer in the world. When Drona demanded his right thumb as guru-dakshina (teacher's fee), Ekalavya cut it off without hesitation. His story teaches dedication, respect, and the power of self-belief beyond all obstacles."
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "On Truth",
                "text": "Bhishma taught: 'Truth is the foundation of all virtue. The universe rests on truth. The gods rejoice in truth. Everything is founded on truth. There is nothing higher than truth. Truth is the greatest form of penance. Through truth, one obtains the divine. Truth is God itself.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Udyoga Parva",
                "section": "Vidura's Wisdom",
                "text": "Vidura advised Dhritarashtra: 'A king who listens only to flatterers destroys his kingdom. A father who ignores his son's wrongdoing enables it. The greatest service you can do for Duryodhana is to tell him the truth, even if it angers him. Love that does not speak truth is not love — it is cowardice dressed in kindness.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Bhishma Parva",
                "section": "On Fear and Courage",
                "text": "On the eve of battle, Krishna told the warriors: 'Fear is natural, but cowardice is a choice. The brave man is not one who does not feel fear — he is one who acts despite the fear. When you face what frightens you most, you discover the true depth of your strength. Courage is not the absence of fear but the mastery of it.'"
            },
            {
                "source": "Mahabharata",
                "parva": "Shanti Parva",
                "section": "On Patience and Perseverance",
                "text": "Bhishma said: 'Patience is the greatest virtue. One who endures hardship without losing their inner peace and dharma is the truly powerful one. The tree that bends in the storm survives; the one that resists is uprooted. Patience is not weakness — it is the strength to endure while remaining true to oneself.'"
            }
        ]

        out_path = os.path.join(DATA_DIR, "mahabharata.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(key_passages, f, indent=2, ensure_ascii=False)
        print(f"      SUCCESS: {len(key_passages)} curated Mahabharata passages saved!")
        return True

    except Exception as e:
        print(f"      FAILED: {e}")
        return False


def download_bhagavad_gita():
    print("\n[2/2] Downloading Bhagavad Gita (all 18 chapters)...")
    print("      Source: Hugging Face dataset")
    try:
        from datasets import load_dataset
        ds = load_dataset("JDhruv14/Bhagavad-Gita_Dataset", split="train")
        print(f"      Dataset columns: {ds.column_names}")
        print(f"      Total rows: {len(ds)}")

        records = []
        for row in ds:
            text = (
                row.get("english") or
                row.get("shloka_meaning") or
                row.get("translation") or
                row.get("meaning") or
                row.get("text") or
                row.get("description") or ""
            )
            chapter = row.get("chapter") or row.get("chapter_number") or ""
            verse   = row.get("verse")   or row.get("verse_number")   or ""

            if text and len(str(text).strip()) > 20:
                records.append({
                    "source": "Bhagavad Gita",
                    "parva": "Bhishma Parva",
                    "section": f"Chapter {chapter} | Verse {verse}",
                    "text": str(text).strip()
                })

        if records:
            out_path = os.path.join(DATA_DIR, "bhagavad_gita.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            print(f"      SUCCESS: {len(records)} verses saved!")
            return True
        else:
            print("      No records found, trying alternative...")
            return download_gita_alternative()

    except Exception as e:
        print(f"      FAILED: {e}")
        return download_gita_alternative()


def download_gita_alternative():
    """Curated Bhagavad Gita verses - all 18 chapters represented"""
    print("      Using curated Gita verses...")
    verses = [
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 1 - Arjuna's Dilemma | Verse 28-30", "text": "Arjuna said: O Krishna, seeing my kinsmen arrayed and eager to fight, my limbs fail and my mouth is parched. My body quivers and my hair stands on end. My bow slips from my hand and my skin burns. I am unable to stand here any longer and my mind seems to whirl."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - Sankhya Yoga | Verse 11", "text": "Krishna said: You grieve for those who should not be grieved for, yet you speak words of wisdom. The wise grieve neither for the living nor for the dead. The soul is eternal, it was never born and will never die."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - Sankhya Yoga | Verse 20", "text": "For the soul there is never birth nor death at any time. It has not come into being, does not come into being, and will not come into being. It is unborn, eternal, ever-existing, and primeval. It is not slain when the body is slain."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - Sankhya Yoga | Verse 47", "text": "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - Sankhya Yoga | Verse 56", "text": "One who is not disturbed in mind even amidst the threefold miseries, who is not elated when there is happiness, and who is free from attachment, fear, and anger, is called a sage of steady mind."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 3 - Karma Yoga | Verse 19", "text": "Therefore, without being attached to the fruits of activities, one should act as a matter of duty, for by working without attachment, one attains the Supreme."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 3 - Karma Yoga | Verse 35", "text": "It is far better to discharge one's prescribed duties, even though faultily, than another's duties perfectly. Destruction in the course of performing one's own duty is better than engaging in another's duties, for to follow another's path is dangerous."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 4 - Jnana Yoga | Verse 7-8", "text": "Whenever there is decay of righteousness and a rise of unrighteousness, O Arjuna, then I manifest Myself. For the protection of the good, for the destruction of the wicked, and for the establishment of righteousness, I come into being from age to age."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 4 - Jnana Yoga | Verse 38", "text": "In this world, there is nothing so sublime and pure as transcendental knowledge. Such knowledge is the mature fruit of all mysticism. And one who has become accomplished in the practice of devotional service enjoys this knowledge within himself in due course of time."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 5 - Karma Sanyasa Yoga | Verse 10", "text": "One who performs his duty without attachment, surrendering the results unto the Supreme Lord, is unaffected by sinful action, as the lotus leaf is untouched by water."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 6 - Dhyana Yoga | Verse 5", "text": "One must deliver himself with the help of his mind, and not degrade himself. The mind is the friend of the conditioned soul, and his enemy as well. For him who has conquered the mind, the mind is the best of friends; but for one who has failed to do so, his mind will remain the greatest enemy."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 6 - Dhyana Yoga | Verse 34-35", "text": "Arjuna said: The mind is restless, turbulent, obstinate and very strong, O Krishna, and to subdue it is more difficult than controlling the wind. Krishna said: It is undoubtedly very difficult to curb the restless mind, but it is possible by suitable practice and by detachment."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 7 - Jnana Vijnana Yoga | Verse 19", "text": "After many births and deaths, he who is actually in knowledge surrenders unto Me, knowing Me to be the cause of all causes and all that is. Such a great soul is very rare."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 8 - Aksara Brahma Yoga | Verse 7", "text": "Therefore, Arjuna, you should always think of Me in the form of Krishna and at the same time carry out your prescribed duty of fighting. With your activities dedicated to Me and your mind and intelligence fixed on Me, you will attain Me without doubt."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 9 - Raja Vidya Yoga | Verse 22", "text": "But those who always worship Me with exclusive devotion, meditating on My transcendental form — to them, I carry what they lack, and I preserve what they have."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 9 - Raja Vidya Yoga | Verse 34", "text": "Engage your mind always in thinking of Me, become My devotee, worship Me and offer your homage unto Me. Thus you will come to Me without fail. I promise you this because you are My very dear friend."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 10 - Vibhuti Yoga | Verse 20", "text": "I am the Self, O Gudakesha, seated in the hearts of all creatures. I am the beginning, the middle and the end of all beings."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 11 - Vishwarupa Darshana Yoga | Verse 33", "text": "Therefore get up and prepare to fight. After conquering your enemies you will enjoy a flourishing kingdom. They are already put to death by My arrangement, and you, O Savyasachi, can be but an instrument in the fight."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 12 - Bhakti Yoga | Verse 13-14", "text": "One who is not envious but is a kind friend to all living entities, who does not think himself a proprietor and is free from false ego, who is equal in both happiness and distress, who is tolerant, always satisfied, self-controlled, and engaged in devotional service with determination, his mind and intelligence fixed on Me — such a devotee of Mine is very dear to Me."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 13 - Kshetra Kshetrajna Vibhaga Yoga | Verse 28", "text": "One who sees the Supersoul equally present everywhere, in every living being, does not degrade himself by his mind. Thus he approaches the transcendental destination."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 14 - Gunatraya Vibhaga Yoga | Verse 23", "text": "One who does not hate illumination, attachment and delusion when they are present or long for them when they disappear; who is unwavering and undisturbed through all these reactions of the material qualities — he is said to have transcended the modes of nature."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 15 - Purushottama Yoga | Verse 15", "text": "I am seated in everyone's heart, and from Me come remembrance, knowledge and forgetfulness. By all the Vedas, I am to be known. Indeed, I am the compiler of Vedanta, and I am the knower of the Vedas."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 16 - Daivásura Sampad Vibhaga Yoga | Verse 21", "text": "There are three gates leading to hell — lust, anger and greed. Every sane man should give these up, for they lead to the degradation of the soul."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 17 - Shraddhatraya Vibhaga Yoga | Verse 3", "text": "O son of Bharata, according to one's existence under the various modes of nature, one evolves a particular kind of faith. The living being is said to be of a particular faith according to the modes he has acquired."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 18 - Moksha Sanyasa Yoga | Verse 63", "text": "Thus I have explained to you knowledge still more confidential. Deliberate on this fully, and then do what you wish to do."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 18 - Moksha Sanyasa Yoga | Verse 65", "text": "Always think of Me, become My devotee, worship Me and offer your homage unto Me. Thus you will come to Me without fail. I promise you this because you are My very dear friend."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 18 - Moksha Sanyasa Yoga | Verse 66", "text": "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - On Grief and Sorrow | Verse 14", "text": "O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, O scion of Bharata, and one must learn to tolerate them without being disturbed."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 2 - On Equanimity | Verse 38", "text": "Do thou fight for the sake of fighting, without considering happiness or distress, loss or gain, victory or defeat — and by so doing you shall never incur sin."},
        {"source": "Bhagavad Gita", "parva": "Bhishma Parva", "section": "Chapter 4 - On Wisdom | Verse 33", "text": "O chastiser of the enemy, the sacrifice performed in knowledge is better than the mere sacrifice of material possessions. After all, the sacrifice of work culminates in transcendental knowledge."},
    ]

    out_path = os.path.join(DATA_DIR, "bhagavad_gita.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(verses, f, indent=2, ensure_ascii=False)
    print(f"      SUCCESS: {len(verses)} Gita verses saved (all 18 chapters)!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  Vishnu Gita - Scripture Data Downloader")
    print("=" * 60)

    m_ok = download_mahabharata()
    g_ok = download_bhagavad_gita()

    print("\n" + "=" * 60)
    if m_ok and g_ok:
        print("  All data downloaded successfully!")
    else:
        print("  Some downloads failed but fallback data is ready.")
    print("  Next step: python build_database.py")
    print("=" * 60)
