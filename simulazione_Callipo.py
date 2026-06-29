import random
import math

# ==============================================================================
# CONFIGURAZIONE PARAMETRI OPERATIVI - CALLIPO AGRICOLA (PIZZO CALABRO, VV)
# ==============================================================================
# Mappatura dei parametri operativi per la raccolta manuale/agevolata:
# - resa_oraria: quintali (q) medi raccolti da una squadra di operai in un'ora.
# - squadre_disponibili: numero massimo di squadre operative assegnabili nei campi.
# - ore_lavorative_giorno: durata del turno giornaliero operativo in Calabria.
PARAMETRI_PRODOTTI = {
    "Olive":  {"resa_oraria": 2.5, "squadre_disponibili": 5},
    "Arance": {"resa_oraria": 4.0, "squadre_disponibili": 4},
    "Fichi":  {"resa_oraria": 1.5, "squadre_disponibili": 3}
}

ORE_LAVORATIVE_GIORNO = 8   # Turno di lavoro standard per il benessere agricolo.
ORGANICO_TOTALE_SQUADRE = 8  # Massimo numero di squadre impiegabili in contemporanea.

# ==============================================================================
# FUNZIONE 1: GENERAZIONE CASUALE DEI LOTTI DI RACCOLTA (STAGIONE AGRICOLA)
# ==============================================================================
def genera_quantita_lotti():
    """
    Genera casualmente le quantità in quintali da raccogliere per i 3 prodotti,
    simulando le fluttuazioni climatiche e le rese dei terreni di Callipo Agricola.
    """
    lotti = {
        "Olive":  random.randint(150, 350),  # Lotto casuale tra 150 e 350 quintali
        "Arance": random.randint(200, 500),  # Lotto casuale tra 200 e 500 quintali
        "Fichi":  random.randint(80, 200)    # Lotto casuale tra 80 e 200 quintali
    }
    return lotti

# ==============================================================================
# FUNZIONE 2: SEQUENZA PRODUTTIVA 1 - RACCOLTA IN SERIE (LINEARE)
# ==============================================================================
def simulazione_sequenza_seriale(lotti_da_raccogliere):
    """
    Simula lo scenario in cui Callipo raccoglie un prodotto alla volta.
    Le squadre dedicate si concentrano interamente sul primo frutto, poi passano al successivo.
    """
    ore_totali = 0
    report_dettagliato = {}
    
    for prodotto, quantita in lotti_da_raccogliere.items():
        resa_oraria_singola = PARAMETRI_PRODOTTI[prodotto]["resa_oraria"]
        squadre = PARAMETRI_PRODOTTI[prodotto]["squadre_disponibili"]
        
        # Resa complessiva oraria della forza lavoro assegnata a quel prodotto
        resa_oraria_totale = resa_oraria_singola * squadre
        
        # Calcolo del tempo necessario per completare la raccolta del lotto
        ore_necessarie = quantita / resa_oraria_totale
        ore_totali += ore_necessarie
        
        report_dettagliato[prodotto] = round(ore_necessarie, 2)
        
    return round(ore_totali, 2), report_dettagliato

# ==============================================================================
# FUNZIONE 3: SEQUENZA PRODUTTIVA 2 - RACCOLTA IN PARALLELO (MULTITASKING)
# ==============================================================================
def simulazione_sequenza_parallela(lotti_da_raccogliere):
    """
    Simula lo scenario in cui le squadre lavorano in contemporanea su più campi,
    dividendo l'organico aziendale totale proporzionalmente alla grandezza dei lotti.
    """
    ore_totali_parallelo = 0
    report_dettagliato = {}
    quantita_totale_lotto = sum(lotti_da_raccogliere.values())
    
    for prodotto, quantita in lotti_da_raccogliere.items():
        resa_oraria_singola = PARAMETRI_PRODOTTI[prodotto]["resa_oraria"]
        
        # Ripartizione matematica delle squadre in base al peso del singolo raccolto
        percentuale_peso = quantita / quantita_totale_lotto
        squadre_assegnate = max(1, round(ORGANICO_TOTALE_SQUADRE * percentuale_peso))
        
        resa_oraria_totale = resa_oraria_singola * squadre_assegnate
        ore_necessarie = quantita / resa_oraria_totale
        
        report_dettagliato[prodotto] = round(ore_necessarie, 2)
        
        # In parallelo, il tempo di blocco finale dipende dal prodotto più lento a finire
        if ore_necessarie > ore_totali_parallelo:
            ore_totali_parallelo = ore_necessarie
            
    return round(ore_totali_parallelo, 2), report_dettagliato

# ==============================================================================
# FUNZIONE PRINCIPALE: COORDINAMENTO DELLA SIMULAZIONE
# ==============================================================================
def main():
    print("-" * 75)
    print("SISTEMA DI PIANIFICAZIONE LOGISTICA RACCOLTA - CALLIPO AGRICOLA S.r.l.")
    print("-" * 75)
    
    # 1. Generazione del dataset casuale dei raccolti calabresi
    lotti_attuali = genera_quantita_lotti()
    print("\n[INFO] Stima quantitativi di raccolta generati per la stagione corrente:")
    for prod, qta in lotti_attuali.items():
        print(f" - Comparto {prod}: {qta} quintali (q)")
        
    # 2. Esecuzione e calcolo dello Scenario 1 (Seriale)
    ore_totali_s1, dettaglio_s1 = simulazione_sequenza_seriale(lotti_attuali)
    giorni_s1 = math.ceil(ore_totali_s1 / ORE_LAVORATIVE_GIORNO)
    
    # 3. Esecuzione e calcolo dello Scenario 2 (Parallelo)
    ore_totali_s2, dettaglio_s2 = simulazione_sequenza_parallela(lotti_attuali)
    giorni_s2 = math.ceil(ore_totali_s2 / ORE_LAVORATIVE_GIORNO)
    
    # 4. Presentazione dei Risultati di Output richiesti dalla traccia
    print("\n" + "="*27 + " ANALISI DI PRODUTTIVITÀ " + "="*27)
    
    print(f"\nSEQUENZA 1 - RACCOLTA IN SERIE (Lineare per comparto):")
    for prod, ore in dettaglio_s1.items():
        print(f" -> Tempo completamento {prod}: {ore} ore")
    print(f"** TEMPO COMPLESSIVO SCENARIO 1: {ore_totali_s1} ore (~{giorni_s1} giorni lavorativi) **")
    
    print(f"\nSEQUENZA 2 - RACCOLTA IN PARALLELO (Contemporanea ottimizzata):")
    for prod, ore in dettaglio_s2.items():
        print(f" -> Tempo completamento {prod}: {ore} ore (in simultanea)")
    print(f"** TEMPO COMPLESSIVO SCENARIO 2: {ore_totali_s2} ore (~{giorni_s2} giorni lavorativi) **")
    print("-" * 75)
    
    # Analisi finale di stampo gestionale per la relazione
    if ore_totali_s2 < ore_totali_s1:
        risparmio = round(ore_totali_s1 - ore_totali_s2, 2)
        print(f"EFFICIENZA: La gestione in Parallelo riduce i tempi di fermo di {risparmio} ore.")
        print("RACCOMANDAZIONE: Adottare la Sequenza 2 per preservare la freschezza delle materie prime.")
    else:
        risparmio = round(ore_totali_s2 - ore_totali_s1, 2)
        print(f"EFFICIENZA: La gestione in Serie risulta più efficiente di {risparmio} ore.")
        print("RACCOMANDAZIONE: Adottare la Sequenza 1 per evitare colli di bottiglia causati dalla scarsità di squadre.")
    print("-" * 75)

if __name__ == "__main__":
    main()