import asyncio
from bleak import BleakGATTCharacteristic, BleakGATTService, BleakGATTServer

class BLEManager:
    def __init__(self):
        self.service_uuid = ""              #Add service uuid here
        self.characteristic_uuid = ""       #Add characteristic uui here
        self.server = BleakGATTServer()
        self.characteristic = None

    async def _on_read(self, characteristic):
        """Callback para leitura de característica."""
        print("Cliente leu a característica!")
        # Retorna dados em bytes
        return b"Hello from Raspberry Pi!"

    async def _on_write(self, characteristic, value):
        """Callback para escrita na característica."""
        print(f"Cliente escreveu na característica: {value.decode('utf-8')}")

    def setup(self):
        """Configura o serviço e as características."""
        service = BleakGATTService(self.service_uuid)

        self.characteristic = BleakGATTCharacteristic(
            self.characteristic_uuid,
            ["read", "write"],
            read_callback=self._on_read,
            write_callback=self._on_write,
        )
        service.add_characteristic(self.characteristic)
        self.server.add_service(service)

    async def start(self):
        """Inicia o servidor BLE."""
        print("Inicializando servidor BLE...")
        await self.server.start()
        print(f"Servidor BLE iniciado com UUID: {self.service_uuid}")
        try:
            await asyncio.sleep(3600)  # Mantém o servidor ativo por 1 hora
        # Remove o servidor BLE quando o usuário pressiona tecla ou CTRL+C ?
        except KeyboardInterrupt:
            print("Encerrando servidor BLE...")
        finally:
            await self.stop()

    async def stop(self):
        """Para o servidor BLE."""
        print("Parando o servidor BLE...")
        await self.server.stop()
