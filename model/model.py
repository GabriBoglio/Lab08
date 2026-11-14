from database.distributore_DAO import DistributoreDAO

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese: int):
        risultato = []
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]
            if prezzi_mese:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, round(media, 3)))
        return risultato

    def get_sequenza_ottima(self, mese: int):
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for id_distributore, lista_prezzi in prezzi_settimana.items():
            costo_spostamento = 5 if (ultimo_distributore is not None and ultimo_distributore != id_distributore) else 0
            costo_carburante = lista_prezzi[giorno - 1] * 100
            nuovo_costo = costo_corrente + costo_spostamento + costo_carburante

            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_filtrati = [p for p in prezzi if p.data.month == mese and p.data.day <= 7]
            prezzi_filtrati.sort(key=lambda p: p.data.day)
            prezzi_settimana[distributore.id] = [p.prezzo_litro for p in prezzi_filtrati]
        return prezzi_settimana