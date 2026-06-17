# infusion_pump_simulation

## Requirements

- Docker
- Git

---

## Clone repository

```bash
git clone <url-del-repo>
cd <nombre-del-repo>
```

---

## Build Docker image

You have to do this only the first time, or everytime you change the Docker.

```bash
docker build -t simulacion-bomba .
```

---

## Execute Simulation

In `pump_proyect/`:

```bash
docker run --rm -it \
    -v $(pwd):/app \
    simulacion-bomba
```

If the simulations runs without errors related with PythonDEVS or dependencis, the instalattion is correct

