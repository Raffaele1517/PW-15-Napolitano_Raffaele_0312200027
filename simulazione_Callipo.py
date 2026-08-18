import math
import random


PARAMETRI_PRODOTTI = {
    "Olive": {"resa_oraria": 2.5, "squadre_max": 5, "deperibilita": 2},
    "Arance": {"resa_oraria": 4.0, "squadre_max": 4, "deperibilita": 3},
    "Fichi": {"resa_oraria": 1.5, "squadre_max": 3, "deperibilita": 5}
}

ORE_LAVORATIVE_GIORNO = 8
ORGANICO_TOTALE_SQUADRE = 8
TRATTORI_DISPONIBILI = 4
SQUADRE_SUPPORTATE_PER_TRATTORE = 2

PENALE_COLLO_BOTTIGLIA = 0.15
COEFF_DETERIORAMENTO = 0.012
PENALITA_MAX_DETERIORAMENTO = 0.60
GIORNI_OBIETTIVO_COMPLETAMENTO = 2

RANDOM_SEED = None


def genera_quantita_lotti():
    return {
        "Olive": random.randint(150, 350),
        "Arance": random.randint(200, 500),
        "Fichi": random.randint(80, 200)
    }


def formatta_ora_lavorativa(ore_da_inizio):
    if ore_da_inizio < 0:
        ore_da_inizio = 0

    resto = ore_da_inizio % ORE_LAVORATIVE_GIORNO

    if ore_da_inizio > 0 and math.isclose(resto, 0, abs_tol=1e-9):
        giorno = int(ore_da_inizio // ORE_LAVORATIVE_GIORNO)
        ora, minuti = 16, 0
    else:
        giorno = int(ore_da_inizio // ORE_LAVORATIVE_GIORNO) + 1
        ora_decimale = 8 + resto
        ora = int(ora_decimale)
        minuti = int(round((ora_decimale - ora) * 60))
        if minuti == 60:
            ora += 1
            minuti = 0

    return f"Giorno {giorno} - {ora:02d}:{minuti:02d}"


def ordina_lotti_per_criterio(lotti_da_raccogliere, criterio="STANDARD"):
    criterio = criterio.upper()

    if criterio == "STANDARD":
        return list(lotti_da_raccogliere.items())

    if criterio == "DEPERIBILITA":
        return sorted(
            lotti_da_raccogliere.items(),
            key=lambda elemento: PARAMETRI_PRODOTTI[elemento[0]]["deperibilita"],
            reverse=True
        )

    raise ValueError(f"Criterio di ordinamento non valido: {criterio!r}")


def calcola_squadre_necessarie(prodotto, quantita):
    # squadre necessarie in funzione della quantita' reale del lotto,
    # capate al tetto di squadre abilitate per il prodotto
    parametri = PARAMETRI_PRODOTTI[prodotto]
    capacita_squadra_periodo = parametri["resa_oraria"] * ORE_LAVORATIVE_GIORNO * GIORNI_OBIETTIVO_COMPLETAMENTO
    necessarie = max(1, math.ceil(quantita / capacita_squadra_periodo))
    return min(necessarie, parametri["squadre_max"])


def ripartisci_risorsa_intera(pesi, totale_risorsa, minimo_per_lotto=0, limiti_massimi=None):
    prodotti = list(pesi.keys())
    assegnazione = {prodotto: 0 for prodotto in prodotti}

    if totale_risorsa <= 0:
        return assegnazione

    if limiti_massimi is None:
        limiti_massimi = {prodotto: totale_risorsa for prodotto in prodotti}

    if minimo_per_lotto > 0:
        for prodotto in sorted(prodotti, key=lambda p: pesi[p], reverse=True):
            if totale_risorsa <= 0:
                break
            if assegnazione[prodotto] < limiti_massimi.get(prodotto, totale_risorsa):
                assegnazione[prodotto] += 1
                totale_risorsa -= 1

    while totale_risorsa > 0:
        candidati = [p for p in prodotti if assegnazione[p] < limiti_massimi.get(p, totale_risorsa)]
        if not candidati:
            break
        prodotto_scelto = max(candidati, key=lambda p: pesi[p] / (assegnazione[p] + 1))
        assegnazione[prodotto_scelto] += 1
        totale_risorsa -= 1

    return assegnazione


def assegna_trattori(squadre_assegnate, trattori_pool_disponibili):
    necessari = math.ceil(squadre_assegnate / SQUADRE_SUPPORTATE_PER_TRATTORE)
    return min(necessari, trattori_pool_disponibili, TRATTORI_DISPONIBILI)


def calcola_penalita_deterioramento(deperibilita, ore_attesa):
    # tempo aggiuntivo dovuto al deperimento del prodotto durante l'attesa
    penalita = COEFF_DETERIORAMENTO * deperibilita * ore_attesa
    return min(penalita, PENALITA_MAX_DETERIORAMENTO)


def simulazione_sequenza_seriale(lotti_da_raccogliere, criterio="STANDARD"):
    ore_totali = 0.0
    report_dettagliato = {}

    lotti_ordinati = ordina_lotti_per_criterio(lotti_da_raccogliere, criterio)

    for prodotto, quantita in lotti_ordinati:
        parametri = PARAMETRI_PRODOTTI[prodotto]

        squadre_necessarie = calcola_squadre_necessarie(prodotto, quantita)
        squadre_effettive = min(squadre_necessarie, ORGANICO_TOTALE_SQUADRE)
        if squadre_effettive <= 0:
            raise ValueError(f"Risorsa 'squadre' insufficiente per lavorare {prodotto}.")

        trattori_assegnati = assegna_trattori(squadre_effettive, TRATTORI_DISPONIBILI)
        squadre_massime_supportate = trattori_assegnati * SQUADRE_SUPPORTATE_PER_TRATTORE
        squadre_effettive = min(squadre_effettive, max(squadre_massime_supportate, 1))

        resa_oraria_totale = parametri["resa_oraria"] * squadre_effettive
        ore_base = quantita / resa_oraria_totale

        # l'attesa dipende dall'ordine di lavorazione: e' questo che lega
        # la sequenza scelta al risultato finale
        ora_inizio = ore_totali
        penalita = calcola_penalita_deterioramento(parametri["deperibilita"], ora_inizio)
        ore_effettive = ore_base * (1 + penalita)
        ora_fine = ora_inizio + ore_effettive

        report_dettagliato[prodotto] = {
            "quantita_q": quantita,
            "deperibilita": parametri["deperibilita"],
            "squadre_effettive": squadre_effettive,
            "trattori_assegnati": trattori_assegnati,
            "attesa_h": round(ora_inizio, 2),
            "penalita_deterioramento_%": round(penalita * 100, 1),
            "ore_lavorazione": round(ore_effettive, 2),
            "inizio_calendario": formatta_ora_lavorativa(ora_inizio),
            "fine_calendario": formatta_ora_lavorativa(ora_fine)
        }

        ore_totali = ora_fine

    return round(ore_totali, 2), report_dettagliato


def simulazione_sequenza_parallela(lotti_da_raccogliere):
    report_dettagliato = {}

    if ORGANICO_TOTALE_SQUADRE < len(lotti_da_raccogliere):
        raise ValueError("Risorsa condivisa 'squadre' insufficiente per il numero di prodotti.")

    limiti_squadre = {p: PARAMETRI_PRODOTTI[p]["squadre_max"] for p in lotti_da_raccogliere}
    squadre_assegnate = ripartisci_risorsa_intera(
        pesi=dict(lotti_da_raccogliere),
        totale_risorsa=ORGANICO_TOTALE_SQUADRE,
        minimo_per_lotto=1,
        limiti_massimi=limiti_squadre
    )

    pesi_trattori = {p: max(squadre_assegnate[p], 1) for p in lotti_da_raccogliere}
    trattori_assegnati = ripartisci_risorsa_intera(
        pesi=pesi_trattori,
        totale_risorsa=TRATTORI_DISPONIBILI,
        minimo_per_lotto=1
    )

    ore_totali_parallelo = 0.0

    for prodotto, quantita in lotti_da_raccogliere.items():
        parametri = PARAMETRI_PRODOTTI[prodotto]
        squadre = squadre_assegnate[prodotto]
        trattori = trattori_assegnati[prodotto]

        resa_oraria_totale = parametri["resa_oraria"] * squadre
        ore_base = quantita / resa_oraria_totale

        capacita_trattori = trattori * SQUADRE_SUPPORTATE_PER_TRATTORE
        collo_bottiglia = squadre > capacita_trattori
        ore_effettive = ore_base * (1 + PENALE_COLLO_BOTTIGLIA) if collo_bottiglia else ore_base

        report_dettagliato[prodotto] = {
            "quantita_q": quantita,
            "deperibilita": parametri["deperibilita"],
            "squadre_assegnate": squadre,
            "trattori_assegnati": trattori,
            "collo_bottiglia": "SI (+15% tempo)" if collo_bottiglia else "NO",
            "ore_lavorazione": round(ore_effettive, 2),
            "inizio_calendario": formatta_ora_lavorativa(0),
            "fine_calendario": formatta_ora_lavorativa(ore_effettive)
        }

        ore_totali_parallelo = max(ore_totali_parallelo, ore_effettive)

    return round(ore_totali_parallelo, 2), report_dettagliato


def _stampa_intestazione(titolo):
    print("\n" + "=" * 90)
    print(f" {titolo}")
    print("=" * 90)


def stampa_report_seriale(titolo, ore_totali, dettaglio):
    _stampa_intestazione(titolo)
    print(f"{'PRODOTTO':<10} | {'Q.TA (q)':<8} | {'DEP.':<4} | {'ATTESA h':<9} | "
          f"{'PENALITA':<9} | {'SQUADRE':<7} | {'TRATT.':<6} | {'INIZIO':<15} | {'FINE':<15} | {'DURATA'}")
    print("-" * 90)
    for p, d in dettaglio.items():
        print(f"{p:<10} | {d['quantita_q']:<8} | {d['deperibilita']:<4} | {d['attesa_h']:<9} | "
              f"{d['penalita_deterioramento_%']:>7}% | {d['squadre_effettive']:<7} | "
              f"{d['trattori_assegnati']:<6} | {d['inizio_calendario']:<15} | {d['fine_calendario']:<15} | "
              f"{d['ore_lavorazione']} h")
    print("-" * 90)
    giorni = math.ceil(ore_totali / ORE_LAVORATIVE_GIORNO)
    print(f"TEMPO TOTALE: {ore_totali} ore  -->  STIMA: ~{giorni} giornate lavorative")


def stampa_report_parallelo(titolo, ore_totali, dettaglio):
    _stampa_intestazione(titolo)
    print(f"{'PRODOTTO':<10} | {'Q.TA (q)':<8} | {'SQUADRE':<7} | {'TRATT.':<6} | "
          f"{'COLLO BOTTIGLIA':<18} | {'COMPLETAMENTO':<15} | {'DURATA'}")
    print("-" * 90)
    for p, d in dettaglio.items():
        print(f"{p:<10} | {d['quantita_q']:<8} | {d['squadre_assegnate']:<7} | {d['trattori_assegnati']:<6} | "
              f"{d['collo_bottiglia']:<18} | {d['fine_calendario']:<15} | {d['ore_lavorazione']} h")
    print("-" * 90)
    giorni = math.ceil(ore_totali / ORE_LAVORATIVE_GIORNO)
    print(f"TEMPO TOTALE: {ore_totali} ore  -->  STIMA: ~{giorni} giornate lavorative")


def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    print("=" * 90)
    print(" SISTEMA DI PIANIFICAZIONE LOGISTICA RACCOLTA - CALLIPO AGRICOLA S.r.l.")
    print("=" * 90)

    lotti_attuali = genera_quantita_lotti()

    print("\n[QUANTITATIVI DI RACCOLTA GENERATI]")
    for p, q in lotti_attuali.items():
        print(f" - {p:<8}: {q} quintali (Deperibilita': {PARAMETRI_PRODOTTI[p]['deperibilita']}/5)")

    print("\n[RISORSE AZIENDALI CONDIVISE]")
    print(f" - Squadre Totali: {ORGANICO_TOTALE_SQUADRE} | Flotta Trattori: {TRATTORI_DISPONIBILI}")

    ore_s1_std, det_s1_std = simulazione_sequenza_seriale(lotti_attuali, "STANDARD")
    ore_s1_dep, det_s1_dep = simulazione_sequenza_seriale(lotti_attuali, "DEPERIBILITA")
    ore_s2, det_s2 = simulazione_sequenza_parallela(lotti_attuali)

    stampa_report_seriale("SCENARIO 1A: RACCOLTA SERIALE (Sequenza Standard)", ore_s1_std, det_s1_std)
    stampa_report_seriale("SCENARIO 1B: RACCOLTA SERIALE (Priorita' Deperibilita')", ore_s1_dep, det_s1_dep)
    stampa_report_parallelo("SCENARIO 2: RACCOLTA PARALLELA (Risorse Condivise)", ore_s2, det_s2)

    print("\n" + "=" * 90)
    print(" SINTESI E CONFRONTO SCENARI")
    print("=" * 90)
    risultati = {
        "Seriale Standard": ore_s1_std,
        "Seriale Priorita' Deperibilita'": ore_s1_dep,
        "Parallelo Risorse Condivise": ore_s2
    }
    for nome, ore in risultati.items():
        print(f" - {nome:<32}: {ore} ore")
    print("-" * 90)

    migliore = min(risultati, key=risultati.get)
    print(f" RISULTATO OTTIMALE: {migliore} con {risultati[migliore]} ore complessive.")
    print("=" * 90)


if __name__ == "__main__":
    main()
