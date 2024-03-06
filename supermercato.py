from threading import Thread, Semaphore
import random
import json # importazione libreria json per la gestione di file json
import threading
import time
import xml.etree.ElementTree as ET # importazione libreria xml per la gestione di file xml

lock = threading.Lock() # creazione del lock

class Cliente(Thread):
    def __init__(self, nome, cognome, conto):
        Thread.__init__(self) # inizializzazione thread
        self.nome = nome
        self.cognome = cognome
        self.conto = conto # conto corrente cliente
        self.carrello = []
        self.pagato = False
        self.volte = 0

    def entra(self):
        if len(supermercato.clienti) < supermercato.capienza: # controllo capienza supermercato
            supermercato.aggiungi_cliente(self) # richiamo metodo aggiungi_cliente della classe Supermercato
            print(self.nome + " è entrato nel supermercato")
        else:
            print("Il supermercato è pieno")

    def esce(self):
        print(self.nome + " è uscito dal supermercato")
        supermercato.rimuovi_cliente(self) # cliente rimosso dal supermercato

    def run(self):
        incasso = []
        spesa = 0.0
        incasso_tot = 0.0
        quant = 0

        lock.acquire() # blocca l’accesso alla sezione di codice seguente fino a quando il lock non viene rilasciato
        print(self.nome + " sta facendo la spesa")
        lock.release() # rilascio lock

        while(self.volte < 3): # gira 3 volte per simulare 3 eventi (6 secondi)
            scelta = random.randint(1,3) # scelta random tra 1 e 3 degli eventi
            if(scelta == 1):
                spesa = 0.0
                prodotto = random.choice(supermercato.prodotti) # scelta random di un prodotto del supermercato
                self.carrello.append(prodotto) # aggiunta prodotto al carrello
                lock.acquire() # blocca l’accesso alla sezione di codice seguente fino a quando il lock non viene rilasciato
                try:
                    print(f"{self.nome} sta comprando {prodotto['nome']}")
                    quant = input("Quanti ne vuoi? ") # input quantità prodotto
                finally:
                    lock.release() # rilascio il lock per permettere ad altri thread di accedere alla sezione di codice bloccata
                prodotto['quantita'] = int(prodotto['quantita']) - int(quant) # scalo quantità prodotto dal magazzino
                for prodotto in self.carrello:
                    spesa = float(quant) * float(prodotto['prezzo']) # calcolo spesa di un cliente
                incasso.append(spesa) # aggiunta spesa all'incasso per quel cliente
            if(scelta == 2):
                lock.acquire()
                try:
                    richiesta = input(f"{self.nome} non sta trovando il prodotto desiderato: ") # input prodotto desiderato ma non trovato dal cliente
                    reparto = supermercato.trova_reparto(richiesta) # richiamo metodo trova_reparto della classe Supermercato
                    if reparto: # se il reparto è presente
                        print(f'Per trovare {richiesta} vai al reparto: {reparto}') # stampa reparto del prodotto
                    else:
                        print('Prodotto non trovato')
                finally:
                    lock.release()
            if(scelta == 3):
                if len(self.carrello) == 0: # se il carrello è vuoto, scegli un altro evento
                    scelta = random.randint(1,2) # scelta random tra eventi 1 e 2
                else:
                    lock.acquire()
                    try:
                        print(f"La spesa di {self.nome} è {self.carrello}")
                        err = input(f"{self.nome} ha sbagliato a prendere un prodotto e lo rimette a posto: ") # input prodotto da rimuovere
                        prodotto_rim = None # creo prodotto da rimuovere
                        for prodotto in self.carrello: # scorro carrello
                            if(err == prodotto['nome']): # controllo se il prodotto da rimuovere è uguale ad un prodotto nel carrello
                                prodotto_rim = prodotto # il prodotto da rimuovere è uguale al prodotto nel carrello
                                self.carrello.remove(prodotto_rim) # rimuovo prodotto dal carrello
                                prodotto['quantita'] = int(prodotto['quantita']) + 1
                                spesa_rimossa = float(prodotto['prezzo']) # calcolo la spesa del prodotto rimosso
                                incasso.remove(spesa_rimossa) # sottraggo la spesa del prodotto rimosso dall'incasso
                            else:
                                print("Prodotto non trovato")
                    finally:
                        lock.release()

            self.volte = self.volte + 1
            time.sleep(2)

        lock.acquire()
        try:
            print(self.nome + " ha finito di fare la spesa")
            incasso_tot = sum(incasso) # calcolo incasso totale della giornata di un cliente
            t = supermercato.aggiorna_totale(incasso_tot) # richiamo metodo aggiorna_totale della classe Supermercato per calcolare il totale di tutti i clienti
            root = ET.Element("incasso") # creo elemento radice incasso
            totale = ET.SubElement(root, "totale") # creo elemento totale
            totale.text = str(t) # come totale scrivo l'incasso totale di tutti i clienti
            tree = ET.ElementTree(root)
            tree.write("incasso.xml") # scrivo il file xml con l'incasso totale
            
            for prodotto in self.carrello:
                print(self.nome + " ha comprato " + str(prodotto['nome'])) # stampa prodotti comprati
            print(self.nome + " ha speso " + str(incasso_tot)) # stampa spesa totale

        finally:
            lock.release()
        cassa_r = random.choice(supermercato.casse) # scelta random di una cassa
        cassa_r.paga(self, incasso_tot) # richiamo metodo paga della classe Cassa

class Supermercato():
    def __init__(self, nome, indirizzo, città, capienza):
        self.nome = nome
        self.indirizzo = indirizzo
        self.città = città
        self.capienza = capienza
        self.clienti = [] # lista clienti del supermercato
        self.casse = [Cassa(1), Cassa(2), Cassa(3)]  # lista casse del supermercato
        self.prodotti = [] # lista prodotti disponibili nel supermercato
        self.total = 0.0

    def aggiungi_cliente(self, cliente): # metodo per aggiungere cliente alla lista clienti
        if len(self.clienti) < self.capienza: # controllo capienza supermercato
            self.clienti.append(cliente) # aggiunta cliente alla lista clienti
        else:
            print("Il supermercato è pieno") # stampa messaggio se supermercato pieno

    def rimuovi_cliente(self, cliente):
        self.clienti.remove(cliente) # rimozione cliente dalla lista clienti

    def carica_prodotti(self, file_path):
        with open(file_path, 'r') as f: # apri json e carica dati
            data = json.load(f)
        for prodotto in data: # scorro prodotti
            self.prodotti.append(prodotto) # aggiungo prodotto alla lista prodotti
            # print(self.prodotti)
        
    def trova_reparto(self, nome_prodotto):
        for prodotto in self.prodotti: # scorro prodotti
            if prodotto["nome"] == nome_prodotto: # controllo se il prodotto inserito è presente nella lista prodotti
                return prodotto["reparto"] # prendo il reparto del prodotto
        return None
    
    def aggiorna_totale(self, incasso_tot):
        self.total += incasso_tot  # aggiorna il totale del supermercato
        return self.total # ritorna il totale del supermercato

class Cassa():
    def __init__(self, numero):
        self.numero = numero
        self.mutex = threading.Lock()  # creo mutex l'accesso esclusivo alla cassa
        self.libera = True  # imposta cassa come libera

    def test_and_set(self):
        with self.mutex: # acquisisce l'accesso esclusivo alla cassa
            stato = self.libera # salva il valore corrente della cassa
            self.libera = False # imposta la cassa come occupata
            return stato # ritorna il valore corrente della cassa

    def paga(self, cliente, incasso_tot):
        while True:
            if self.test_and_set():  # se la cassa è libera, cliente paga
                print(f"Cassa {self.numero} occupata") # cassa occupata perchè c'è un cliente
                print(f"{cliente.nome} sta pagando {incasso_tot} alla cassa {self.numero}")
                time.sleep(5)  # tempo per pagare
                if cliente.conto < incasso_tot: # controllo conto cliente
                    print(f"{cliente.nome} non ha abbastanza soldi")
                else:
                    print(f"{cliente.nome} ha pagato {incasso_tot} alla cassa {self.numero}")
                    cliente.pagato = True # cliente ha pagato
                self.libera = True  # imposta cassa come libera
                break

print("BENVENUTI AL SUPERMERCATO!!")
nome_supermercato = input("Inserisci il nome del supermercato: ")
indirizzo = input("Inserisci l'indirizzo: ")
città = input("Inserisci la città: ")
capienza = int(input("Inserisci la capienza massima del supermercato: "))
supermercato = Supermercato(nome_supermercato, indirizzo, città, capienza)
supermercato.carica_prodotti("Supermercato/magazzino.json") # carica prodotti dal file scritto nel percorso

while(len(supermercato.clienti) < supermercato.capienza): # gira finchè la capienza del supermercato non è raggiunta
    nome = input("Inserisci il nome del cliente: ")
    cognome = input("Inserisci il cognome del cliente: ")
    conto = float(input("Quanto ha nel conto corrente: "))
    cliente = Cliente(nome, cognome, conto) # creazione cliente
    cliente.entra() # cliente entra nel supermercato
    print("Vuoi aggiungere un altro cliente? (s/n)") # s = si, n = no
    agg = input()
    if ((agg == 'n')): # se l'utente non vuole aggiungere altri clienti, esco dal while
        break
    elif len(supermercato.clienti) >= supermercato.capienza: # controllo capienza
        print("Il supermercato è pieno")
        break

for cliente in supermercato.clienti: # scorro clienti
    cliente.start() # avvio thread cliente
for cliente in supermercato.clienti: # scorro clienti
    cliente.join() # attendo la terminazione del thread cliente
for cliente in supermercato.clienti: # scorro clienti
    cliente.esce() # clienti escono dal supermercato
