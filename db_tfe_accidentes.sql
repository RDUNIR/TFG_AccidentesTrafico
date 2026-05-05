--
-- PostgreSQL database dump
--

\restrict H7gKyXFOf6h4CNs2FXuqvYz83fuiz6IW8lpAAkWZrc80N2Z2ENbhJG3O20QXp4t

-- Dumped from database version 16.13 (Homebrew)
-- Dumped by pg_dump version 18.2

-- Started on 2026-05-05 13:47:33 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 224 (class 1259 OID 16419)
-- Name: accidentes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accidentes (
    id integer NOT NULL,
    fecha date NOT NULL,
    hora time without time zone NOT NULL,
    carretera_id integer,
    gravedad_id integer,
    causa_id integer,
    clima_id integer,
    num_vehiculos integer DEFAULT 1,
    num_heridos integer DEFAULT 0,
    num_fallecidos integer DEFAULT 0,
    observaciones text
);


ALTER TABLE public.accidentes OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16418)
-- Name: accidentes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accidentes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accidentes_id_seq OWNER TO postgres;

--
-- TOC entry 3873 (class 0 OID 0)
-- Dependencies: 223
-- Name: accidentes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accidentes_id_seq OWNED BY public.accidentes.id;


--
-- TOC entry 216 (class 1259 OID 16391)
-- Name: carreteras; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carreteras (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    tipo character varying(50)
);


ALTER TABLE public.carreteras OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16390)
-- Name: carreteras_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.carreteras_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.carreteras_id_seq OWNER TO postgres;

--
-- TOC entry 3874 (class 0 OID 0)
-- Dependencies: 215
-- Name: carreteras_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.carreteras_id_seq OWNED BY public.carreteras.id;


--
-- TOC entry 218 (class 1259 OID 16398)
-- Name: causas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.causas (
    id integer NOT NULL,
    descripcion character varying(100) NOT NULL
);


ALTER TABLE public.causas OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16397)
-- Name: causas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.causas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.causas_id_seq OWNER TO postgres;

--
-- TOC entry 3875 (class 0 OID 0)
-- Dependencies: 217
-- Name: causas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.causas_id_seq OWNED BY public.causas.id;


--
-- TOC entry 220 (class 1259 OID 16405)
-- Name: clima; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clima (
    id integer NOT NULL,
    descripcion character varying(50) NOT NULL
);


ALTER TABLE public.clima OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16404)
-- Name: clima_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clima_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clima_id_seq OWNER TO postgres;

--
-- TOC entry 3876 (class 0 OID 0)
-- Dependencies: 219
-- Name: clima_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clima_id_seq OWNED BY public.clima.id;


--
-- TOC entry 222 (class 1259 OID 16412)
-- Name: gravedad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gravedad (
    id integer NOT NULL,
    nivel character varying(50) NOT NULL
);


ALTER TABLE public.gravedad OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16411)
-- Name: gravedad_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gravedad_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gravedad_id_seq OWNER TO postgres;

--
-- TOC entry 3877 (class 0 OID 0)
-- Dependencies: 221
-- Name: gravedad_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gravedad_id_seq OWNED BY public.gravedad.id;


--
-- TOC entry 3697 (class 2604 OID 16422)
-- Name: accidentes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes ALTER COLUMN id SET DEFAULT nextval('public.accidentes_id_seq'::regclass);


--
-- TOC entry 3693 (class 2604 OID 16394)
-- Name: carreteras id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreteras ALTER COLUMN id SET DEFAULT nextval('public.carreteras_id_seq'::regclass);


--
-- TOC entry 3694 (class 2604 OID 16401)
-- Name: causas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.causas ALTER COLUMN id SET DEFAULT nextval('public.causas_id_seq'::regclass);


--
-- TOC entry 3695 (class 2604 OID 16408)
-- Name: clima id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clima ALTER COLUMN id SET DEFAULT nextval('public.clima_id_seq'::regclass);


--
-- TOC entry 3696 (class 2604 OID 16415)
-- Name: gravedad id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gravedad ALTER COLUMN id SET DEFAULT nextval('public.gravedad_id_seq'::regclass);


--
-- TOC entry 3867 (class 0 OID 16419)
-- Dependencies: 224
-- Data for Name: accidentes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accidentes (id, fecha, hora, carretera_id, gravedad_id, causa_id, clima_id, num_vehiculos, num_heridos, num_fallecidos, observaciones) FROM stdin;
1	2026-03-24	09:57:00	1	4	11	8	10	2	2	Maniobra evasiva resultando en choque lateral.
2	2025-03-19	16:29:00	2	2	10	8	15	6	0	Incidente en tramo recto con asfalto seco.
3	2025-05-01	22:15:00	3	3	8	8	13	7	0	Atestado pendiente de completar por la unidad de tráfico.
4	2026-02-08	18:03:00	4	1	8	7	11	8	0	Atestado pendiente de completar por la unidad de tráfico.
5	2025-10-04	18:32:00	5	2	7	7	7	10	0	Colisión por alcance en zona de visibilidad reducida.
6	2025-08-18	10:06:00	6	3	11	8	18	3	0	Salida de vía por posible distracción del conductor.
7	2025-09-26	21:09:00	7	1	9	7	6	9	0	Atestado pendiente de completar por la unidad de tráfico.
8	2025-08-10	01:34:00	8	4	12	9	6	3	1	Salida de vía por posible distracción del conductor.
9	2025-06-19	22:15:00	9	1	8	10	12	9	0	Incidente en tramo recto con asfalto seco.
10	2026-02-02	16:47:00	10	3	11	7	18	10	0	Salida de vía por posible distracción del conductor.
11	2026-03-04	10:08:00	11	2	11	9	17	5	0	Colisión por alcance en zona de visibilidad reducida.
12	2026-02-01	14:35:00	12	3	10	8	8	1	0	Maniobra evasiva resultando en choque lateral.
13	2026-01-14	16:54:00	13	3	8	6	2	2	0	Incidente en tramo recto con asfalto seco.
14	2026-03-09	13:36:00	14	3	7	9	18	1	0	Salida de vía por posible distracción del conductor.
15	2026-02-24	07:59:00	15	3	12	10	3	3	0	Salida de vía por posible distracción del conductor.
16	2025-11-01	20:10:00	16	1	7	6	19	9	0	Incidente en tramo recto con asfalto seco.
17	2026-03-17	05:03:00	17	2	11	6	16	3	0	Colisión por alcance en zona de visibilidad reducida.
18	2025-09-04	14:58:00	18	3	8	7	20	3	0	Colisión por alcance en zona de visibilidad reducida.
19	2025-04-26	19:07:00	19	3	8	8	9	7	0	Colisión por alcance en zona de visibilidad reducida.
20	2025-11-02	00:00:00	20	1	10	6	18	2	0	Colisión por alcance en zona de visibilidad reducida.
21	2026-01-23	12:36:00	21	2	10	10	8	8	0	Incidente en tramo recto con asfalto seco.
22	2025-10-04	04:23:00	22	1	12	8	3	9	0	Colisión por alcance en zona de visibilidad reducida.
23	2025-05-11	20:45:00	23	2	8	6	2	7	0	Salida de vía por posible distracción del conductor.
24	2025-01-10	03:26:00	24	2	12	9	10	2	0	Salida de vía por posible distracción del conductor.
25	2025-08-24	17:07:00	25	3	9	9	8	8	0	Colisión por alcance en zona de visibilidad reducida.
26	2026-01-31	23:19:00	26	1	8	9	19	4	0	Atestado pendiente de completar por la unidad de tráfico.
27	2025-01-22	04:47:00	27	4	10	6	3	1	2	Salida de vía por posible distracción del conductor.
28	2025-07-11	22:39:00	28	4	10	7	9	3	1	Maniobra evasiva resultando en choque lateral.
29	2025-06-15	19:49:00	29	1	11	10	17	3	0	Atestado pendiente de completar por la unidad de tráfico.
30	2025-09-06	21:48:00	30	3	12	10	2	1	0	Atestado pendiente de completar por la unidad de tráfico.
31	2026-03-14	03:41:00	31	1	9	6	8	8	0	Maniobra evasiva resultando en choque lateral.
32	2026-01-21	11:04:00	32	2	12	6	18	3	0	Maniobra evasiva resultando en choque lateral.
33	2025-10-03	04:57:00	33	2	9	7	5	8	0	Maniobra evasiva resultando en choque lateral.
34	2025-09-18	01:59:00	34	3	8	9	3	3	0	Salida de vía por posible distracción del conductor.
35	2025-12-20	12:13:00	35	3	9	10	19	9	0	Atestado pendiente de completar por la unidad de tráfico.
36	2025-10-12	05:01:00	36	1	8	10	20	7	0	Colisión por alcance en zona de visibilidad reducida.
37	2025-02-14	14:45:00	37	2	12	8	15	5	0	Maniobra evasiva resultando en choque lateral.
38	2026-01-25	08:59:00	38	4	8	7	17	3	2	Incidente en tramo recto con asfalto seco.
39	2025-08-07	02:20:00	39	4	8	10	4	3	2	Salida de vía por posible distracción del conductor.
40	2026-03-27	21:32:00	40	1	12	6	4	1	0	Colisión por alcance en zona de visibilidad reducida.
41	2025-12-15	13:53:00	41	2	9	7	6	2	0	Salida de vía por posible distracción del conductor.
42	2025-01-16	16:18:00	42	2	9	8	3	3	0	Atestado pendiente de completar por la unidad de tráfico.
43	2025-10-02	20:36:00	43	3	9	6	10	7	0	Incidente en tramo recto con asfalto seco.
44	2025-09-06	03:46:00	44	4	8	6	17	2	1	Maniobra evasiva resultando en choque lateral.
45	2025-02-12	01:30:00	45	1	8	9	10	10	0	Maniobra evasiva resultando en choque lateral.
46	2025-12-16	05:14:00	46	2	10	9	16	9	0	Colisión por alcance en zona de visibilidad reducida.
47	2025-05-09	16:30:00	47	1	12	7	13	1	0	Maniobra evasiva resultando en choque lateral.
48	2025-12-18	21:53:00	48	4	12	9	11	4	2	Atestado pendiente de completar por la unidad de tráfico.
49	2025-08-16	03:50:00	49	3	9	10	11	2	0	Maniobra evasiva resultando en choque lateral.
50	2025-12-06	15:28:00	50	1	8	7	12	9	0	Colisión por alcance en zona de visibilidad reducida.
51	2025-09-10	14:54:00	51	2	9	7	18	7	0	Incidente en tramo recto con asfalto seco.
52	2026-02-05	15:11:00	25	2	7	7	7	7	0	Salida de vía por posible distracción del conductor.
53	2026-02-10	08:35:00	50	1	10	6	11	8	0	Salida de vía por posible distracción del conductor.
54	2025-10-03	15:36:00	43	2	7	10	9	3	0	Atestado pendiente de completar por la unidad de tráfico.
55	2025-07-09	07:39:00	12	3	12	7	14	10	0	Salida de vía por posible distracción del conductor.
56	2025-05-03	02:07:00	3	2	9	10	2	7	0	Maniobra evasiva resultando en choque lateral.
57	2025-04-23	21:36:00	45	3	12	10	10	5	0	Colisión por alcance en zona de visibilidad reducida.
58	2025-06-11	21:00:00	40	1	9	8	1	6	0	Salida de vía por posible distracción del conductor.
59	2025-09-13	08:12:00	35	2	11	9	4	8	0	Colisión por alcance en zona de visibilidad reducida.
60	2025-09-07	23:44:00	35	4	10	7	8	3	1	Salida de vía por posible distracción del conductor.
61	2025-06-17	23:21:00	49	1	11	7	6	9	0	Maniobra evasiva resultando en choque lateral.
62	2025-01-25	22:39:00	27	3	11	7	16	8	0	Incidente en tramo recto con asfalto seco.
63	2025-11-07	10:58:00	19	1	9	8	15	9	0	Salida de vía por posible distracción del conductor.
64	2025-08-24	21:50:00	27	1	11	9	18	7	0	Colisión por alcance en zona de visibilidad reducida.
65	2025-10-03	05:28:00	12	2	10	10	3	4	0	Atestado pendiente de completar por la unidad de tráfico.
66	2025-05-20	06:01:00	3	4	9	9	3	2	2	Salida de vía por posible distracción del conductor.
67	2025-01-04	18:02:00	32	2	12	10	10	2	0	Colisión por alcance en zona de visibilidad reducida.
68	2025-01-01	11:48:00	47	2	12	8	15	8	0	Colisión por alcance en zona de visibilidad reducida.
69	2026-02-18	11:25:00	8	3	12	9	10	10	0	Atestado pendiente de completar por la unidad de tráfico.
70	2026-02-22	00:36:00	20	2	8	6	19	7	0	Maniobra evasiva resultando en choque lateral.
71	2026-02-15	04:58:00	8	1	11	9	17	9	0	Incidente en tramo recto con asfalto seco.
72	2025-02-25	05:22:00	18	1	7	8	11	9	0	Incidente en tramo recto con asfalto seco.
73	2025-02-23	16:20:00	3	1	10	10	15	6	0	Salida de vía por posible distracción del conductor.
74	2025-01-02	18:32:00	45	2	11	7	6	10	0	Maniobra evasiva resultando en choque lateral.
75	2025-12-22	09:14:00	9	2	11	10	1	5	0	Colisión por alcance en zona de visibilidad reducida.
76	2025-06-19	18:22:00	24	2	8	8	10	1	0	Colisión por alcance en zona de visibilidad reducida.
77	2025-10-26	20:58:00	17	2	10	10	5	9	0	Maniobra evasiva resultando en choque lateral.
78	2026-01-04	11:25:00	14	1	11	7	14	5	0	Colisión por alcance en zona de visibilidad reducida.
79	2025-06-04	13:30:00	39	1	10	7	9	8	0	Incidente en tramo recto con asfalto seco.
80	2025-05-19	14:12:00	35	1	12	7	3	7	0	Maniobra evasiva resultando en choque lateral.
81	2025-11-11	10:16:00	39	4	11	8	18	1	1	Colisión por alcance en zona de visibilidad reducida.
82	2025-10-19	19:03:00	42	4	11	7	7	5	1	Maniobra evasiva resultando en choque lateral.
83	2026-03-02	19:34:00	20	2	12	9	13	4	0	Colisión por alcance en zona de visibilidad reducida.
84	2025-03-29	18:47:00	46	1	10	10	20	6	0	Maniobra evasiva resultando en choque lateral.
85	2025-07-02	19:36:00	44	3	10	6	19	10	0	Atestado pendiente de completar por la unidad de tráfico.
86	2025-07-25	01:28:00	22	1	9	9	1	2	0	Incidente en tramo recto con asfalto seco.
87	2025-08-15	23:52:00	6	1	12	7	18	2	0	Maniobra evasiva resultando en choque lateral.
88	2026-03-03	07:39:00	36	1	7	9	8	10	0	Salida de vía por posible distracción del conductor.
89	2025-02-03	07:33:00	16	2	9	8	4	2	0	Atestado pendiente de completar por la unidad de tráfico.
90	2025-11-01	17:32:00	22	3	7	8	12	10	0	Maniobra evasiva resultando en choque lateral.
91	2025-09-06	22:30:00	24	3	10	9	9	6	0	Salida de vía por posible distracción del conductor.
92	2025-11-15	17:08:00	16	2	7	9	6	4	0	Atestado pendiente de completar por la unidad de tráfico.
93	2025-03-14	05:57:00	8	2	12	7	17	1	0	Incidente en tramo recto con asfalto seco.
94	2025-10-15	01:17:00	3	3	7	8	14	4	0	Salida de vía por posible distracción del conductor.
95	2025-03-05	16:29:00	12	2	11	6	10	8	0	Colisión por alcance en zona de visibilidad reducida.
96	2025-05-05	06:04:00	1	2	7	10	12	2	0	Atestado pendiente de completar por la unidad de tráfico.
97	2026-01-17	23:08:00	13	3	8	7	15	5	0	Incidente en tramo recto con asfalto seco.
98	2025-01-15	00:10:00	4	3	12	7	8	10	0	Atestado pendiente de completar por la unidad de tráfico.
99	2025-11-14	15:34:00	13	2	10	10	9	3	0	Incidente en tramo recto con asfalto seco.
100	2025-05-05	21:18:00	4	2	7	8	2	1	0	Atestado pendiente de completar por la unidad de tráfico.
101	2025-08-18	17:42:00	7	4	10	6	19	4	1	Incidente en tramo recto con asfalto seco.
102	2025-03-07	12:40:00	22	2	9	6	12	1	0	Colisión por alcance en zona de visibilidad reducida.
103	2025-07-09	02:33:00	17	1	10	7	19	4	0	Atestado pendiente de completar por la unidad de tráfico.
104	2025-10-30	12:31:00	13	1	7	9	6	1	0	Atestado pendiente de completar por la unidad de tráfico.
105	2025-06-25	00:44:00	8	1	12	6	15	8	0	Atestado pendiente de completar por la unidad de tráfico.
106	2025-09-09	05:25:00	46	2	7	10	15	8	0	Atestado pendiente de completar por la unidad de tráfico.
107	2025-03-15	17:19:00	49	4	11	10	6	3	1	Maniobra evasiva resultando en choque lateral.
108	2025-03-04	09:25:00	45	1	11	9	17	10	0	Colisión por alcance en zona de visibilidad reducida.
109	2025-03-06	19:48:00	31	2	7	10	19	1	0	Incidente en tramo recto con asfalto seco.
110	2025-05-28	03:13:00	37	2	10	9	9	2	0	Colisión por alcance en zona de visibilidad reducida.
111	2025-07-13	21:58:00	21	3	12	8	17	5	0	Atestado pendiente de completar por la unidad de tráfico.
112	2025-05-25	22:48:00	45	2	8	8	1	5	0	Incidente en tramo recto con asfalto seco.
113	2025-05-10	22:38:00	5	1	10	8	20	4	0	Salida de vía por posible distracción del conductor.
114	2025-02-08	13:03:00	24	4	8	7	5	5	1	Atestado pendiente de completar por la unidad de tráfico.
115	2025-05-10	21:51:00	27	3	7	8	5	2	0	Colisión por alcance en zona de visibilidad reducida.
116	2026-01-19	14:59:00	25	3	10	10	17	5	0	Maniobra evasiva resultando en choque lateral.
117	2025-07-21	02:01:00	20	3	8	8	20	9	0	Incidente en tramo recto con asfalto seco.
118	2025-09-27	21:30:00	18	1	7	7	6	6	0	Colisión por alcance en zona de visibilidad reducida.
119	2026-02-28	11:36:00	2	2	7	9	11	9	0	Atestado pendiente de completar por la unidad de tráfico.
120	2025-03-08	23:50:00	11	3	12	10	16	6	0	Colisión por alcance en zona de visibilidad reducida.
121	2025-10-09	12:14:00	30	3	9	10	10	7	0	Maniobra evasiva resultando en choque lateral.
122	2025-05-21	00:20:00	47	4	11	6	14	3	2	Atestado pendiente de completar por la unidad de tráfico.
123	2025-07-17	15:34:00	51	2	7	10	9	3	0	Incidente en tramo recto con asfalto seco.
124	2025-07-10	03:33:00	25	2	11	7	17	9	0	Maniobra evasiva resultando en choque lateral.
125	2025-01-05	04:19:00	6	1	8	8	5	9	0	Colisión por alcance en zona de visibilidad reducida.
126	2025-05-07	16:04:00	4	3	12	6	8	5	0	Salida de vía por posible distracción del conductor.
127	2025-11-19	09:42:00	44	1	10	10	16	3	0	Maniobra evasiva resultando en choque lateral.
128	2025-06-01	06:30:00	13	3	7	10	19	1	0	Incidente en tramo recto con asfalto seco.
129	2026-01-17	13:03:00	48	2	12	10	4	5	0	Atestado pendiente de completar por la unidad de tráfico.
130	2025-11-12	01:55:00	10	4	8	8	15	4	1	Incidente en tramo recto con asfalto seco.
131	2025-10-01	01:57:00	21	2	12	7	4	8	0	Maniobra evasiva resultando en choque lateral.
132	2026-02-26	12:03:00	35	1	7	8	16	3	0	Colisión por alcance en zona de visibilidad reducida.
133	2025-03-26	02:26:00	24	1	10	8	12	8	0	Salida de vía por posible distracción del conductor.
134	2026-03-31	10:09:00	2	2	8	7	11	6	0	Atestado pendiente de completar por la unidad de tráfico.
135	2025-08-05	00:42:00	1	1	7	10	20	4	0	Salida de vía por posible distracción del conductor.
136	2025-10-19	21:10:00	45	4	10	7	10	2	2	Incidente en tramo recto con asfalto seco.
137	2025-06-01	18:52:00	19	2	9	6	18	8	0	Incidente en tramo recto con asfalto seco.
138	2026-03-31	06:25:00	48	2	9	10	14	1	0	Incidente en tramo recto con asfalto seco.
139	2025-12-30	11:38:00	45	1	8	6	15	8	0	Colisión por alcance en zona de visibilidad reducida.
140	2025-07-17	14:52:00	35	2	7	7	9	1	0	Colisión por alcance en zona de visibilidad reducida.
141	2026-01-19	13:06:00	23	3	8	6	6	6	0	Incidente en tramo recto con asfalto seco.
142	2025-08-12	03:31:00	30	3	8	6	19	4	0	Incidente en tramo recto con asfalto seco.
143	2025-03-31	07:25:00	29	2	10	9	1	6	0	Salida de vía por posible distracción del conductor.
144	2025-05-25	00:34:00	29	1	8	8	4	5	0	Incidente en tramo recto con asfalto seco.
145	2026-02-20	18:16:00	12	2	10	8	17	10	0	Incidente en tramo recto con asfalto seco.
146	2025-02-24	17:47:00	7	1	11	7	13	8	0	Maniobra evasiva resultando en choque lateral.
147	2025-10-24	13:18:00	2	4	7	8	5	2	1	Incidente en tramo recto con asfalto seco.
148	2025-08-04	02:23:00	42	3	8	10	8	3	0	Atestado pendiente de completar por la unidad de tráfico.
149	2025-02-01	02:33:00	29	1	9	9	11	5	0	Colisión por alcance en zona de visibilidad reducida.
150	2025-05-12	19:45:00	31	1	7	10	9	8	0	Atestado pendiente de completar por la unidad de tráfico.
151	2025-01-08	14:17:00	29	2	10	9	2	8	0	Maniobra evasiva resultando en choque lateral.
152	2025-02-09	11:15:00	27	2	7	7	7	9	0	Colisión por alcance en zona de visibilidad reducida.
153	2025-02-23	21:25:00	25	3	10	7	17	7	0	Maniobra evasiva resultando en choque lateral.
154	2026-02-15	11:13:00	2	2	9	10	5	6	0	Maniobra evasiva resultando en choque lateral.
155	2025-06-14	15:37:00	14	3	8	8	5	8	0	Incidente en tramo recto con asfalto seco.
156	2026-02-13	07:10:00	33	1	11	10	18	2	0	Incidente en tramo recto con asfalto seco.
157	2025-04-13	18:57:00	39	3	11	9	8	6	0	Colisión por alcance en zona de visibilidad reducida.
158	2025-09-15	09:53:00	38	1	10	6	14	3	0	Salida de vía por posible distracción del conductor.
159	2025-08-02	23:17:00	50	3	7	7	20	7	0	Atestado pendiente de completar por la unidad de tráfico.
160	2025-09-10	00:54:00	1	2	8	8	13	3	0	Incidente en tramo recto con asfalto seco.
161	2026-01-23	01:47:00	19	1	10	9	18	10	0	Incidente en tramo recto con asfalto seco.
162	2025-09-01	23:06:00	31	2	7	10	11	1	0	Colisión por alcance en zona de visibilidad reducida.
163	2025-08-13	22:35:00	49	3	9	7	8	5	0	Salida de vía por posible distracción del conductor.
164	2025-05-12	12:21:00	45	2	7	6	14	8	0	Maniobra evasiva resultando en choque lateral.
165	2025-08-15	20:28:00	4	2	12	10	19	6	0	Atestado pendiente de completar por la unidad de tráfico.
166	2025-03-11	17:36:00	23	4	12	6	13	2	2	Incidente en tramo recto con asfalto seco.
167	2025-02-27	09:27:00	32	2	11	7	15	4	0	Incidente en tramo recto con asfalto seco.
168	2025-06-17	19:21:00	45	2	12	9	11	2	0	Salida de vía por posible distracción del conductor.
169	2025-07-28	15:40:00	40	3	8	9	14	6	0	Salida de vía por posible distracción del conductor.
170	2025-03-04	13:19:00	37	2	9	9	10	3	0	Salida de vía por posible distracción del conductor.
171	2025-08-14	21:16:00	5	1	9	6	4	9	0	Colisión por alcance en zona de visibilidad reducida.
172	2025-04-08	00:42:00	31	3	11	6	1	3	0	Incidente en tramo recto con asfalto seco.
173	2025-10-26	10:02:00	4	1	11	7	13	5	0	Atestado pendiente de completar por la unidad de tráfico.
174	2025-03-07	11:09:00	32	4	8	8	17	1	1	Incidente en tramo recto con asfalto seco.
175	2025-11-10	10:07:00	31	1	11	7	2	10	0	Maniobra evasiva resultando en choque lateral.
176	2025-06-23	02:11:00	49	2	9	9	9	9	0	Maniobra evasiva resultando en choque lateral.
177	2025-11-25	00:13:00	19	3	9	7	6	8	0	Atestado pendiente de completar por la unidad de tráfico.
178	2025-04-06	17:03:00	41	4	8	6	18	1	1	Colisión por alcance en zona de visibilidad reducida.
179	2026-01-27	22:31:00	1	1	11	10	13	9	0	Maniobra evasiva resultando en choque lateral.
180	2025-01-02	12:12:00	41	3	10	7	8	10	0	Salida de vía por posible distracción del conductor.
181	2025-02-10	05:07:00	35	2	11	7	12	6	0	Incidente en tramo recto con asfalto seco.
182	2025-07-30	14:21:00	41	2	9	8	5	10	0	Incidente en tramo recto con asfalto seco.
183	2026-03-12	17:18:00	39	2	11	9	4	9	0	Colisión por alcance en zona de visibilidad reducida.
184	2025-08-09	22:08:00	19	2	9	9	18	5	0	Maniobra evasiva resultando en choque lateral.
185	2025-07-16	14:00:00	13	4	8	10	5	1	1	Salida de vía por posible distracción del conductor.
186	2025-04-20	11:19:00	22	4	9	6	14	2	1	Maniobra evasiva resultando en choque lateral.
187	2026-01-28	02:21:00	22	3	7	8	5	7	0	Atestado pendiente de completar por la unidad de tráfico.
188	2025-04-07	20:23:00	46	1	8	9	5	8	0	Colisión por alcance en zona de visibilidad reducida.
189	2025-02-09	06:05:00	2	1	9	8	9	4	0	Atestado pendiente de completar por la unidad de tráfico.
190	2025-03-02	16:54:00	5	4	8	7	10	5	1	Salida de vía por posible distracción del conductor.
191	2026-01-19	05:44:00	10	2	9	6	12	5	0	Atestado pendiente de completar por la unidad de tráfico.
192	2025-01-13	23:59:00	31	1	12	6	18	9	0	Incidente en tramo recto con asfalto seco.
193	2025-11-27	12:09:00	36	2	7	6	13	8	0	Colisión por alcance en zona de visibilidad reducida.
194	2025-03-10	22:46:00	15	1	9	6	19	7	0	Maniobra evasiva resultando en choque lateral.
195	2025-11-06	05:53:00	35	2	9	6	10	5	0	Salida de vía por posible distracción del conductor.
196	2025-04-08	23:37:00	5	2	9	6	16	5	0	Maniobra evasiva resultando en choque lateral.
197	2025-04-23	19:10:00	37	1	10	9	11	1	0	Incidente en tramo recto con asfalto seco.
198	2025-05-21	10:39:00	17	2	10	10	7	8	0	Incidente en tramo recto con asfalto seco.
199	2025-02-15	09:07:00	5	1	12	7	8	3	0	Salida de vía por posible distracción del conductor.
200	2025-02-04	06:45:00	17	4	10	7	13	4	1	Maniobra evasiva resultando en choque lateral.
201	2025-10-08	13:28:00	49	3	10	7	6	2	0	Colisión por alcance en zona de visibilidad reducida.
202	2025-07-27	23:46:00	33	1	10	6	9	9	0	Incidente en tramo recto con asfalto seco.
203	2026-01-01	15:06:00	19	3	7	7	19	9	0	Maniobra evasiva resultando en choque lateral.
204	2025-02-07	19:24:00	39	1	11	6	9	9	0	Incidente en tramo recto con asfalto seco.
205	2025-03-28	00:03:00	3	2	10	7	9	9	0	Maniobra evasiva resultando en choque lateral.
206	2026-02-18	15:17:00	43	2	10	6	10	1	0	Atestado pendiente de completar por la unidad de tráfico.
207	2026-02-05	20:51:00	45	2	11	10	17	6	0	Colisión por alcance en zona de visibilidad reducida.
208	2026-03-21	22:29:00	44	4	7	10	13	1	2	Atestado pendiente de completar por la unidad de tráfico.
209	2025-11-07	11:26:00	34	4	7	6	14	5	1	Salida de vía por posible distracción del conductor.
210	2026-02-06	08:35:00	31	3	8	9	6	2	0	Colisión por alcance en zona de visibilidad reducida.
211	2025-10-21	08:59:00	24	1	9	10	4	2	0	Maniobra evasiva resultando en choque lateral.
212	2025-09-04	13:45:00	45	1	7	6	4	2	0	Atestado pendiente de completar por la unidad de tráfico.
213	2025-05-29	22:37:00	8	1	12	10	13	9	0	Colisión por alcance en zona de visibilidad reducida.
214	2026-03-23	21:44:00	41	3	11	10	19	2	0	Incidente en tramo recto con asfalto seco.
215	2025-04-02	01:16:00	15	2	11	7	9	5	0	Atestado pendiente de completar por la unidad de tráfico.
216	2025-04-04	01:18:00	23	3	9	9	17	10	0	Maniobra evasiva resultando en choque lateral.
217	2025-06-03	20:00:00	47	2	11	7	6	9	0	Salida de vía por posible distracción del conductor.
218	2025-07-23	21:42:00	33	4	7	9	2	4	1	Incidente en tramo recto con asfalto seco.
219	2026-03-02	23:34:00	24	3	8	6	5	3	0	Incidente en tramo recto con asfalto seco.
220	2026-01-20	10:33:00	27	4	7	7	15	0	1	Maniobra evasiva resultando en choque lateral.
221	2025-09-03	20:22:00	28	1	8	7	10	8	0	Maniobra evasiva resultando en choque lateral.
222	2025-04-02	07:37:00	30	2	10	9	13	10	0	Salida de vía por posible distracción del conductor.
223	2025-07-15	12:21:00	32	1	8	9	12	5	0	Salida de vía por posible distracción del conductor.
224	2025-02-07	15:56:00	3	3	11	9	19	7	0	Atestado pendiente de completar por la unidad de tráfico.
225	2025-10-19	14:23:00	31	2	10	10	5	9	0	Maniobra evasiva resultando en choque lateral.
226	2025-11-10	19:37:00	46	1	11	7	2	3	0	Salida de vía por posible distracción del conductor.
227	2026-01-17	18:52:00	10	3	7	9	8	8	0	Colisión por alcance en zona de visibilidad reducida.
228	2026-02-05	14:50:00	34	3	11	9	15	5	0	Salida de vía por posible distracción del conductor.
229	2025-05-06	17:34:00	2	2	8	7	10	2	0	Salida de vía por posible distracción del conductor.
230	2025-09-27	13:16:00	14	1	9	7	16	5	0	Atestado pendiente de completar por la unidad de tráfico.
231	2025-03-11	01:27:00	14	2	9	6	15	7	0	Colisión por alcance en zona de visibilidad reducida.
232	2025-09-07	11:24:00	26	1	7	7	2	5	0	Incidente en tramo recto con asfalto seco.
233	2025-04-04	08:46:00	29	2	11	10	20	5	0	Salida de vía por posible distracción del conductor.
234	2025-06-30	02:29:00	49	2	11	7	9	3	0	Maniobra evasiva resultando en choque lateral.
235	2025-07-18	04:56:00	38	2	10	7	4	10	0	Maniobra evasiva resultando en choque lateral.
236	2025-05-25	14:02:00	10	3	9	9	19	10	0	Colisión por alcance en zona de visibilidad reducida.
237	2025-02-14	09:10:00	30	2	12	6	17	1	0	Atestado pendiente de completar por la unidad de tráfico.
238	2025-03-11	22:31:00	40	3	9	8	3	1	0	Incidente en tramo recto con asfalto seco.
239	2025-12-24	00:35:00	48	1	12	8	10	4	0	Salida de vía por posible distracción del conductor.
240	2025-11-05	12:37:00	18	3	11	6	11	9	0	Salida de vía por posible distracción del conductor.
241	2025-05-11	14:03:00	24	2	8	8	10	2	0	Salida de vía por posible distracción del conductor.
242	2026-02-17	07:54:00	37	1	12	8	20	4	0	Maniobra evasiva resultando en choque lateral.
243	2025-07-07	06:04:00	47	2	11	6	1	7	0	Atestado pendiente de completar por la unidad de tráfico.
244	2025-10-13	09:02:00	30	3	12	9	12	6	0	Incidente en tramo recto con asfalto seco.
245	2025-09-12	06:58:00	32	2	10	6	3	8	0	Atestado pendiente de completar por la unidad de tráfico.
246	2026-02-04	18:42:00	21	1	11	10	9	1	0	Colisión por alcance en zona de visibilidad reducida.
247	2025-04-14	23:29:00	44	1	12	6	8	8	0	Colisión por alcance en zona de visibilidad reducida.
248	2025-05-29	15:27:00	11	2	8	10	2	3	0	Incidente en tramo recto con asfalto seco.
249	2026-03-04	19:59:00	16	2	8	8	13	5	0	Maniobra evasiva resultando en choque lateral.
250	2025-09-16	12:36:00	9	2	7	9	3	9	0	Colisión por alcance en zona de visibilidad reducida.
251	2025-01-21	20:46:00	18	3	9	9	6	4	0	Salida de vía por posible distracción del conductor.
252	2025-05-31	07:01:00	9	2	10	9	1	3	0	Maniobra evasiva resultando en choque lateral.
253	2025-02-22	01:59:00	44	2	11	10	3	6	0	Colisión por alcance en zona de visibilidad reducida.
254	2025-03-10	16:28:00	6	2	8	6	7	1	0	Atestado pendiente de completar por la unidad de tráfico.
255	2025-08-12	04:29:00	15	1	12	10	1	6	0	Salida de vía por posible distracción del conductor.
256	2026-04-02	07:15:00	9	2	12	7	11	7	0	Maniobra evasiva resultando en choque lateral.
257	2025-08-11	21:40:00	41	2	12	8	7	5	0	Incidente en tramo recto con asfalto seco.
258	2025-04-17	03:57:00	42	1	9	9	14	8	0	Incidente en tramo recto con asfalto seco.
259	2025-11-05	20:57:00	5	2	8	7	17	6	0	Incidente en tramo recto con asfalto seco.
260	2025-11-16	07:13:00	36	3	10	7	12	1	0	Incidente en tramo recto con asfalto seco.
261	2025-06-19	16:17:00	27	3	12	10	7	3	0	Maniobra evasiva resultando en choque lateral.
262	2025-02-10	13:13:00	43	3	9	6	10	8	0	Colisión por alcance en zona de visibilidad reducida.
263	2025-03-29	10:49:00	2	2	7	8	3	1	0	Atestado pendiente de completar por la unidad de tráfico.
264	2026-01-10	14:06:00	4	2	11	10	8	1	0	Maniobra evasiva resultando en choque lateral.
265	2025-03-20	15:29:00	35	2	8	8	14	3	0	Atestado pendiente de completar por la unidad de tráfico.
266	2025-03-02	15:52:00	45	2	10	8	19	8	0	Atestado pendiente de completar por la unidad de tráfico.
267	2025-05-02	11:13:00	20	3	12	9	20	9	0	Maniobra evasiva resultando en choque lateral.
268	2026-03-12	13:54:00	21	2	9	8	11	4	0	Incidente en tramo recto con asfalto seco.
269	2025-12-31	04:34:00	4	3	12	6	20	6	0	Colisión por alcance en zona de visibilidad reducida.
270	2025-12-05	05:56:00	32	2	12	7	5	10	0	Colisión por alcance en zona de visibilidad reducida.
271	2025-10-03	09:29:00	40	2	11	7	3	5	0	Maniobra evasiva resultando en choque lateral.
272	2025-09-09	23:35:00	40	2	7	10	7	7	0	Salida de vía por posible distracción del conductor.
273	2025-10-10	12:53:00	33	2	8	7	13	8	0	Salida de vía por posible distracción del conductor.
274	2025-09-01	21:05:00	36	3	12	6	3	3	0	Atestado pendiente de completar por la unidad de tráfico.
275	2025-06-23	23:59:00	25	2	9	6	3	6	0	Maniobra evasiva resultando en choque lateral.
276	2025-02-01	12:12:00	36	2	11	6	17	10	0	Atestado pendiente de completar por la unidad de tráfico.
277	2025-07-27	06:50:00	1	3	12	6	9	5	0	Salida de vía por posible distracción del conductor.
278	2025-11-27	21:47:00	13	3	10	6	7	6	0	Incidente en tramo recto con asfalto seco.
279	2025-10-31	10:47:00	25	1	11	10	4	10	0	Salida de vía por posible distracción del conductor.
280	2026-02-22	19:52:00	4	3	12	9	15	4	0	Incidente en tramo recto con asfalto seco.
281	2026-02-04	14:14:00	30	3	7	7	6	3	0	Atestado pendiente de completar por la unidad de tráfico.
282	2025-10-12	05:12:00	47	2	9	6	7	10	0	Colisión por alcance en zona de visibilidad reducida.
283	2025-04-26	10:22:00	7	1	11	7	19	7	0	Maniobra evasiva resultando en choque lateral.
284	2026-03-11	08:17:00	34	3	10	9	3	6	0	Incidente en tramo recto con asfalto seco.
285	2025-12-17	04:14:00	28	2	12	10	16	9	0	Incidente en tramo recto con asfalto seco.
286	2025-09-09	01:11:00	46	2	9	7	5	4	0	Colisión por alcance en zona de visibilidad reducida.
287	2025-08-16	02:27:00	15	3	10	10	2	3	0	Colisión por alcance en zona de visibilidad reducida.
288	2025-10-03	04:11:00	31	1	11	6	19	9	0	Maniobra evasiva resultando en choque lateral.
289	2026-03-27	13:44:00	12	3	10	10	18	2	0	Maniobra evasiva resultando en choque lateral.
290	2025-06-09	13:32:00	1	1	8	8	11	10	0	Salida de vía por posible distracción del conductor.
291	2026-01-25	21:41:00	4	3	9	7	17	7	0	Atestado pendiente de completar por la unidad de tráfico.
292	2026-03-16	09:49:00	25	3	8	10	16	9	0	Atestado pendiente de completar por la unidad de tráfico.
293	2025-04-11	22:35:00	32	2	11	9	9	10	0	Maniobra evasiva resultando en choque lateral.
294	2026-04-02	22:34:00	9	1	10	7	8	9	0	Colisión por alcance en zona de visibilidad reducida.
295	2025-02-20	13:16:00	12	3	8	10	16	7	0	Colisión por alcance en zona de visibilidad reducida.
296	2025-02-14	17:23:00	8	1	11	10	9	6	0	Atestado pendiente de completar por la unidad de tráfico.
297	2025-11-13	06:43:00	41	1	7	9	18	3	0	Salida de vía por posible distracción del conductor.
298	2025-01-25	16:08:00	13	1	8	7	11	6	0	Maniobra evasiva resultando en choque lateral.
299	2025-01-18	09:17:00	50	2	7	8	20	5	0	Colisión por alcance en zona de visibilidad reducida.
300	2025-11-28	13:11:00	29	3	9	9	7	9	0	Salida de vía por posible distracción del conductor.
301	2025-08-13	03:54:00	8	3	12	8	2	6	0	Salida de vía por posible distracción del conductor.
302	2026-02-20	01:54:00	46	2	10	6	3	7	0	Atestado pendiente de completar por la unidad de tráfico.
303	2025-12-19	21:23:00	27	2	10	9	1	6	0	Atestado pendiente de completar por la unidad de tráfico.
304	2025-07-01	16:07:00	31	2	10	10	10	6	0	Colisión por alcance en zona de visibilidad reducida.
305	2025-01-15	22:43:00	26	3	9	6	11	3	0	Salida de vía por posible distracción del conductor.
306	2026-01-25	11:44:00	33	3	12	7	20	3	0	Colisión por alcance en zona de visibilidad reducida.
307	2025-08-12	21:47:00	40	1	9	7	9	7	0	Atestado pendiente de completar por la unidad de tráfico.
308	2025-04-09	09:27:00	8	3	10	8	12	3	0	Atestado pendiente de completar por la unidad de tráfico.
309	2026-02-26	04:32:00	2	3	12	9	5	2	0	Colisión por alcance en zona de visibilidad reducida.
310	2025-05-06	12:30:00	34	1	11	8	11	2	0	Maniobra evasiva resultando en choque lateral.
311	2025-10-18	17:59:00	4	2	12	8	3	3	0	Salida de vía por posible distracción del conductor.
312	2025-02-24	09:05:00	1	3	7	7	10	4	0	Maniobra evasiva resultando en choque lateral.
313	2025-03-07	15:00:00	23	3	11	10	19	10	0	Atestado pendiente de completar por la unidad de tráfico.
314	2025-07-04	15:11:00	11	2	8	9	15	1	0	Salida de vía por posible distracción del conductor.
315	2025-01-25	20:15:00	8	2	12	7	11	5	0	Atestado pendiente de completar por la unidad de tráfico.
316	2025-10-23	02:32:00	27	2	11	6	13	1	0	Salida de vía por posible distracción del conductor.
317	2025-12-03	07:27:00	18	3	11	7	14	4	0	Salida de vía por posible distracción del conductor.
318	2025-05-12	03:23:00	23	2	12	6	20	6	0	Salida de vía por posible distracción del conductor.
319	2026-02-08	15:24:00	27	1	10	9	1	9	0	Salida de vía por posible distracción del conductor.
320	2026-01-09	20:01:00	3	1	12	9	9	2	0	Salida de vía por posible distracción del conductor.
321	2025-09-14	22:34:00	48	3	12	8	4	6	0	Colisión por alcance en zona de visibilidad reducida.
322	2025-07-02	00:48:00	31	2	12	9	2	5	0	Incidente en tramo recto con asfalto seco.
323	2025-03-24	18:25:00	51	1	8	9	2	6	0	Salida de vía por posible distracción del conductor.
324	2026-01-03	10:38:00	29	2	9	6	15	9	0	Colisión por alcance en zona de visibilidad reducida.
325	2025-08-30	05:41:00	25	3	11	6	9	4	0	Colisión por alcance en zona de visibilidad reducida.
326	2026-01-01	04:41:00	27	1	11	6	8	3	0	Incidente en tramo recto con asfalto seco.
327	2025-07-31	03:22:00	16	1	9	8	17	3	0	Incidente en tramo recto con asfalto seco.
328	2025-12-11	21:23:00	41	2	12	8	20	4	0	Atestado pendiente de completar por la unidad de tráfico.
329	2026-02-27	01:31:00	5	2	12	6	16	6	0	Incidente en tramo recto con asfalto seco.
330	2025-03-12	12:54:00	39	2	10	8	3	7	0	Colisión por alcance en zona de visibilidad reducida.
331	2026-04-01	11:50:00	37	2	7	6	20	6	0	Incidente en tramo recto con asfalto seco.
332	2025-03-04	10:20:00	30	2	7	8	13	5	0	Colisión por alcance en zona de visibilidad reducida.
333	2025-09-05	09:05:00	40	1	10	10	9	5	0	Salida de vía por posible distracción del conductor.
334	2025-06-23	13:43:00	45	3	9	6	12	2	0	Incidente en tramo recto con asfalto seco.
335	2025-06-03	14:01:00	25	2	11	6	15	1	0	Colisión por alcance en zona de visibilidad reducida.
336	2025-11-11	20:11:00	31	2	9	6	15	6	0	Salida de vía por posible distracción del conductor.
337	2025-07-22	01:16:00	45	3	9	10	6	7	0	Incidente en tramo recto con asfalto seco.
338	2025-06-16	22:51:00	36	2	12	10	13	1	0	Maniobra evasiva resultando en choque lateral.
339	2026-01-15	20:05:00	45	3	12	10	1	5	0	Maniobra evasiva resultando en choque lateral.
340	2025-06-25	10:54:00	12	2	11	7	18	1	0	Atestado pendiente de completar por la unidad de tráfico.
341	2025-06-27	11:33:00	14	1	10	6	13	7	0	Colisión por alcance en zona de visibilidad reducida.
342	2025-06-15	09:01:00	25	3	8	10	11	5	0	Maniobra evasiva resultando en choque lateral.
343	2026-01-25	15:18:00	4	2	9	8	5	10	0	Maniobra evasiva resultando en choque lateral.
344	2025-01-18	08:05:00	20	1	7	8	12	5	0	Incidente en tramo recto con asfalto seco.
345	2025-03-29	00:39:00	13	3	9	8	13	3	0	Maniobra evasiva resultando en choque lateral.
346	2025-10-31	08:28:00	16	1	12	8	2	10	0	Colisión por alcance en zona de visibilidad reducida.
347	2025-11-10	02:12:00	35	2	9	10	8	3	0	Incidente en tramo recto con asfalto seco.
348	2025-04-15	00:02:00	24	1	8	7	7	1	0	Incidente en tramo recto con asfalto seco.
349	2026-01-10	03:36:00	10	1	8	7	6	10	0	Atestado pendiente de completar por la unidad de tráfico.
350	2025-12-30	07:24:00	47	2	12	9	10	10	0	Atestado pendiente de completar por la unidad de tráfico.
351	2025-02-16	07:02:00	2	1	8	7	9	3	0	Colisión por alcance en zona de visibilidad reducida.
352	2025-08-18	12:37:00	3	1	10	6	3	10	0	Salida de vía por posible distracción del conductor.
353	2026-03-11	01:35:00	42	1	9	7	1	10	0	Incidente en tramo recto con asfalto seco.
354	2025-05-06	05:15:00	47	2	9	6	19	1	0	Maniobra evasiva resultando en choque lateral.
355	2025-08-17	01:33:00	43	1	8	7	6	3	0	Salida de vía por posible distracción del conductor.
356	2025-01-28	08:21:00	5	1	8	10	13	9	0	Maniobra evasiva resultando en choque lateral.
357	2025-04-23	21:16:00	6	1	8	6	16	7	0	Salida de vía por posible distracción del conductor.
358	2025-12-20	13:55:00	42	2	7	9	10	10	0	Maniobra evasiva resultando en choque lateral.
359	2026-03-10	18:19:00	10	1	7	9	8	9	0	Maniobra evasiva resultando en choque lateral.
360	2025-10-25	04:42:00	17	1	11	8	13	10	0	Salida de vía por posible distracción del conductor.
361	2025-03-15	09:03:00	27	3	8	10	9	6	0	Maniobra evasiva resultando en choque lateral.
362	2025-11-17	15:11:00	14	2	8	6	17	4	0	Salida de vía por posible distracción del conductor.
363	2025-03-21	15:15:00	7	1	7	8	9	5	0	Maniobra evasiva resultando en choque lateral.
364	2025-07-23	19:58:00	25	3	12	6	10	3	0	Colisión por alcance en zona de visibilidad reducida.
365	2025-11-03	00:34:00	12	3	8	9	10	8	0	Salida de vía por posible distracción del conductor.
366	2025-06-03	13:06:00	18	1	9	6	16	6	0	Atestado pendiente de completar por la unidad de tráfico.
367	2025-05-24	12:48:00	20	2	8	9	10	2	0	Salida de vía por posible distracción del conductor.
368	2026-02-07	19:55:00	30	2	8	6	8	8	0	Maniobra evasiva resultando en choque lateral.
369	2025-03-30	19:56:00	7	2	10	6	2	4	0	Incidente en tramo recto con asfalto seco.
370	2026-02-14	21:11:00	40	2	9	8	13	5	0	Atestado pendiente de completar por la unidad de tráfico.
371	2025-03-30	19:57:00	16	3	8	6	14	8	0	Maniobra evasiva resultando en choque lateral.
372	2025-06-09	08:51:00	27	2	11	9	19	7	0	Incidente en tramo recto con asfalto seco.
373	2025-09-02	10:59:00	36	2	10	10	15	2	0	Salida de vía por posible distracción del conductor.
374	2026-03-26	01:32:00	35	1	7	9	15	2	0	Atestado pendiente de completar por la unidad de tráfico.
375	2025-01-29	11:55:00	42	2	7	6	12	7	0	Atestado pendiente de completar por la unidad de tráfico.
376	2026-03-28	18:27:00	18	3	11	7	3	4	0	Incidente en tramo recto con asfalto seco.
377	2025-11-06	23:35:00	36	2	8	6	10	6	0	Salida de vía por posible distracción del conductor.
378	2025-08-02	09:34:00	6	1	7	6	16	10	0	Salida de vía por posible distracción del conductor.
379	2026-03-14	02:44:00	14	1	7	10	10	9	0	Salida de vía por posible distracción del conductor.
380	2025-07-23	20:01:00	31	2	11	6	16	2	0	Maniobra evasiva resultando en choque lateral.
381	2025-03-28	14:06:00	22	3	7	8	6	8	0	Colisión por alcance en zona de visibilidad reducida.
382	2026-03-29	09:15:00	30	1	10	8	18	10	0	Incidente en tramo recto con asfalto seco.
383	2025-09-20	02:53:00	20	1	9	9	11	3	0	Incidente en tramo recto con asfalto seco.
384	2025-07-19	19:48:00	36	2	9	10	14	8	0	Salida de vía por posible distracción del conductor.
385	2025-06-02	15:58:00	34	2	11	6	10	6	0	Salida de vía por posible distracción del conductor.
386	2025-09-19	11:36:00	10	1	10	10	8	9	0	Atestado pendiente de completar por la unidad de tráfico.
387	2025-12-22	12:36:00	48	2	9	6	9	10	0	Maniobra evasiva resultando en choque lateral.
388	2025-08-02	22:36:00	51	3	12	10	13	4	0	Maniobra evasiva resultando en choque lateral.
389	2025-12-02	03:52:00	20	2	7	7	7	8	0	Atestado pendiente de completar por la unidad de tráfico.
390	2025-12-25	14:15:00	26	1	9	10	11	4	0	Maniobra evasiva resultando en choque lateral.
391	2025-03-22	01:49:00	38	1	8	9	13	6	0	Colisión por alcance en zona de visibilidad reducida.
392	2025-07-06	15:56:00	34	3	7	8	15	10	0	Salida de vía por posible distracción del conductor.
393	2026-01-13	00:56:00	27	1	11	7	13	10	0	Salida de vía por posible distracción del conductor.
394	2025-03-31	16:02:00	43	1	10	9	19	2	0	Colisión por alcance en zona de visibilidad reducida.
395	2026-03-28	14:37:00	42	2	12	7	2	8	0	Incidente en tramo recto con asfalto seco.
396	2025-08-27	21:46:00	45	1	11	6	18	9	0	Salida de vía por posible distracción del conductor.
397	2025-09-06	20:34:00	5	3	7	8	18	7	0	Incidente en tramo recto con asfalto seco.
398	2026-01-02	10:54:00	51	2	11	8	18	10	0	Incidente en tramo recto con asfalto seco.
399	2025-12-25	11:51:00	5	3	7	9	15	6	0	Incidente en tramo recto con asfalto seco.
400	2025-09-07	02:15:00	22	2	11	9	4	6	0	Colisión por alcance en zona de visibilidad reducida.
401	2025-09-29	07:35:00	2	2	8	6	1	5	0	Atestado pendiente de completar por la unidad de tráfico.
402	2025-10-24	07:15:00	3	1	7	8	15	7	0	Salida de vía por posible distracción del conductor.
403	2025-09-17	08:19:00	10	1	12	6	12	1	0	Maniobra evasiva resultando en choque lateral.
404	2026-01-06	19:23:00	28	1	7	8	9	4	0	Colisión por alcance en zona de visibilidad reducida.
405	2025-09-21	06:52:00	11	1	8	8	8	7	0	Colisión por alcance en zona de visibilidad reducida.
406	2025-07-13	01:32:00	45	2	10	7	2	4	0	Colisión por alcance en zona de visibilidad reducida.
407	2025-01-07	01:00:00	32	2	7	8	2	10	0	Salida de vía por posible distracción del conductor.
408	2025-09-21	16:04:00	4	1	11	8	3	10	0	Incidente en tramo recto con asfalto seco.
409	2025-12-03	22:44:00	48	2	8	8	5	4	0	Colisión por alcance en zona de visibilidad reducida.
410	2026-01-25	00:22:00	40	3	10	10	18	6	0	Atestado pendiente de completar por la unidad de tráfico.
411	2025-11-19	22:47:00	7	2	11	7	18	2	0	Colisión por alcance en zona de visibilidad reducida.
412	2025-07-13	11:44:00	29	2	8	10	8	8	0	Atestado pendiente de completar por la unidad de tráfico.
413	2025-03-03	19:00:00	18	3	11	7	3	8	0	Colisión por alcance en zona de visibilidad reducida.
414	2025-08-06	00:38:00	50	1	8	10	9	4	0	Atestado pendiente de completar por la unidad de tráfico.
415	2026-02-07	05:57:00	16	2	9	8	14	7	0	Atestado pendiente de completar por la unidad de tráfico.
416	2025-03-31	09:57:00	49	1	9	7	10	2	0	Salida de vía por posible distracción del conductor.
417	2026-01-03	11:43:00	17	3	8	9	6	7	0	Colisión por alcance en zona de visibilidad reducida.
418	2025-03-15	12:05:00	23	1	10	9	18	6	0	Incidente en tramo recto con asfalto seco.
419	2026-02-06	21:11:00	43	3	12	10	2	10	0	Salida de vía por posible distracción del conductor.
420	2025-11-28	20:46:00	4	2	7	9	15	3	0	Incidente en tramo recto con asfalto seco.
421	2025-06-21	09:36:00	16	3	12	9	8	4	0	Incidente en tramo recto con asfalto seco.
422	2025-08-22	20:39:00	16	2	12	7	14	7	0	Colisión por alcance en zona de visibilidad reducida.
423	2025-12-31	05:25:00	38	2	10	7	13	3	0	Maniobra evasiva resultando en choque lateral.
424	2025-05-31	06:53:00	29	2	8	10	12	6	0	Incidente en tramo recto con asfalto seco.
425	2026-03-27	13:55:00	1	3	9	8	8	3	0	Maniobra evasiva resultando en choque lateral.
426	2025-12-22	06:08:00	42	2	9	6	4	4	0	Salida de vía por posible distracción del conductor.
427	2025-12-09	16:08:00	37	1	10	6	13	6	0	Incidente en tramo recto con asfalto seco.
428	2025-05-04	16:48:00	43	2	11	9	2	4	0	Maniobra evasiva resultando en choque lateral.
429	2025-09-21	12:46:00	11	1	11	8	8	3	0	Atestado pendiente de completar por la unidad de tráfico.
430	2026-03-19	06:19:00	41	1	11	6	2	3	0	Salida de vía por posible distracción del conductor.
431	2025-11-15	14:17:00	1	2	7	7	11	3	0	Atestado pendiente de completar por la unidad de tráfico.
432	2025-05-01	18:55:00	12	1	10	6	15	2	0	Salida de vía por posible distracción del conductor.
433	2026-01-16	17:15:00	5	2	9	7	9	3	0	Colisión por alcance en zona de visibilidad reducida.
434	2026-01-02	20:23:00	1	2	12	7	17	8	0	Maniobra evasiva resultando en choque lateral.
435	2025-03-30	06:21:00	16	2	11	9	12	1	0	Maniobra evasiva resultando en choque lateral.
436	2026-02-01	23:46:00	46	1	11	7	2	2	0	Atestado pendiente de completar por la unidad de tráfico.
437	2025-11-06	09:22:00	33	2	7	7	5	5	0	Colisión por alcance en zona de visibilidad reducida.
438	2026-03-20	10:20:00	28	1	11	6	19	5	0	Salida de vía por posible distracción del conductor.
439	2025-11-13	18:19:00	26	2	8	6	20	2	0	Incidente en tramo recto con asfalto seco.
440	2026-03-03	12:16:00	1	1	9	10	2	8	0	Atestado pendiente de completar por la unidad de tráfico.
441	2025-01-01	23:36:00	5	1	10	7	4	5	0	Maniobra evasiva resultando en choque lateral.
442	2025-08-04	21:31:00	11	1	12	8	17	8	0	Salida de vía por posible distracción del conductor.
443	2025-02-14	00:02:00	15	2	11	8	13	3	0	Maniobra evasiva resultando en choque lateral.
444	2025-11-20	05:19:00	48	3	8	7	7	7	0	Incidente en tramo recto con asfalto seco.
445	2025-07-05	14:10:00	17	2	8	9	19	9	0	Maniobra evasiva resultando en choque lateral.
446	2025-04-03	13:40:00	36	1	7	8	9	6	0	Salida de vía por posible distracción del conductor.
447	2025-08-08	02:38:00	2	2	10	6	12	10	0	Atestado pendiente de completar por la unidad de tráfico.
448	2025-07-04	14:25:00	45	3	10	9	7	7	0	Colisión por alcance en zona de visibilidad reducida.
449	2025-03-21	14:26:00	9	1	10	9	2	9	0	Colisión por alcance en zona de visibilidad reducida.
450	2026-01-30	04:27:00	31	2	12	6	17	3	0	Salida de vía por posible distracción del conductor.
451	2026-01-22	11:39:00	6	2	12	10	8	3	0	Salida de vía por posible distracción del conductor.
452	2026-03-20	16:47:00	39	2	7	10	16	5	0	Atestado pendiente de completar por la unidad de tráfico.
453	2026-03-29	16:00:00	25	2	10	6	19	1	0	Maniobra evasiva resultando en choque lateral.
454	2025-01-28	00:23:00	23	3	7	10	18	4	0	Maniobra evasiva resultando en choque lateral.
455	2025-08-16	12:59:00	44	3	9	6	4	1	0	Salida de vía por posible distracción del conductor.
456	2025-04-01	13:10:00	36	1	8	10	13	8	0	Colisión por alcance en zona de visibilidad reducida.
457	2025-10-13	09:51:00	45	2	10	6	15	7	0	Salida de vía por posible distracción del conductor.
458	2025-03-04	17:13:00	43	3	10	8	10	8	0	Maniobra evasiva resultando en choque lateral.
459	2025-05-27	19:18:00	41	3	7	8	6	6	0	Maniobra evasiva resultando en choque lateral.
460	2025-09-15	08:18:00	38	1	8	7	1	4	0	Salida de vía por posible distracción del conductor.
461	2026-01-12	19:16:00	11	1	7	9	9	5	0	Incidente en tramo recto con asfalto seco.
462	2025-08-13	20:10:00	41	2	8	6	1	7	0	Incidente en tramo recto con asfalto seco.
463	2025-10-05	03:39:00	35	2	10	6	7	7	0	Colisión por alcance en zona de visibilidad reducida.
464	2025-02-13	02:43:00	6	2	9	8	13	7	0	Atestado pendiente de completar por la unidad de tráfico.
465	2025-11-14	01:58:00	41	2	8	10	13	3	0	Colisión por alcance en zona de visibilidad reducida.
466	2025-03-12	01:59:00	4	2	9	8	10	6	0	Colisión por alcance en zona de visibilidad reducida.
467	2025-06-21	10:02:00	24	2	9	8	3	5	0	Maniobra evasiva resultando en choque lateral.
468	2025-09-08	14:18:00	21	2	9	8	16	10	0	Salida de vía por posible distracción del conductor.
469	2025-07-23	01:34:00	34	2	8	10	5	2	0	Incidente en tramo recto con asfalto seco.
470	2025-07-08	23:28:00	2	2	11	9	16	3	0	Salida de vía por posible distracción del conductor.
471	2026-03-09	17:04:00	17	1	10	7	2	3	0	Maniobra evasiva resultando en choque lateral.
472	2025-11-17	01:42:00	12	1	12	8	3	7	0	Incidente en tramo recto con asfalto seco.
473	2025-06-28	13:12:00	46	1	8	9	5	1	0	Maniobra evasiva resultando en choque lateral.
474	2025-03-08	18:49:00	34	1	8	6	11	8	0	Salida de vía por posible distracción del conductor.
475	2025-05-21	06:18:00	31	3	9	9	7	7	0	Atestado pendiente de completar por la unidad de tráfico.
476	2025-01-24	21:43:00	35	3	7	8	12	1	0	Maniobra evasiva resultando en choque lateral.
477	2026-03-07	18:17:00	13	2	12	7	1	3	0	Incidente en tramo recto con asfalto seco.
478	2025-03-04	17:42:00	1	1	9	9	17	10	0	Maniobra evasiva resultando en choque lateral.
479	2026-01-23	08:45:00	3	3	12	7	7	1	0	Salida de vía por posible distracción del conductor.
480	2026-03-25	12:06:00	44	3	7	8	4	3	0	Salida de vía por posible distracción del conductor.
481	2025-06-21	16:56:00	5	1	8	6	4	6	0	Incidente en tramo recto con asfalto seco.
482	2025-09-26	18:52:00	2	3	11	10	13	7	0	Maniobra evasiva resultando en choque lateral.
483	2025-12-16	04:17:00	51	3	7	10	18	3	0	Colisión por alcance en zona de visibilidad reducida.
484	2025-06-01	11:34:00	44	1	7	10	9	4	0	Atestado pendiente de completar por la unidad de tráfico.
485	2025-05-23	13:37:00	29	2	10	7	9	9	0	Salida de vía por posible distracción del conductor.
486	2026-01-05	16:56:00	51	2	12	8	4	9	0	Atestado pendiente de completar por la unidad de tráfico.
487	2025-05-24	19:28:00	17	1	8	6	3	7	0	Colisión por alcance en zona de visibilidad reducida.
488	2025-06-28	20:56:00	28	2	10	10	3	5	0	Salida de vía por posible distracción del conductor.
489	2025-08-17	18:33:00	21	1	9	9	18	2	0	Maniobra evasiva resultando en choque lateral.
490	2025-03-27	03:21:00	17	3	10	9	13	10	0	Atestado pendiente de completar por la unidad de tráfico.
491	2025-12-18	15:19:00	40	1	8	6	7	8	0	Colisión por alcance en zona de visibilidad reducida.
492	2025-12-13	12:54:00	38	2	10	8	9	8	0	Atestado pendiente de completar por la unidad de tráfico.
493	2025-06-08	02:06:00	47	3	7	9	12	5	0	Maniobra evasiva resultando en choque lateral.
494	2025-09-08	03:38:00	30	1	9	7	12	10	0	Atestado pendiente de completar por la unidad de tráfico.
495	2026-03-10	19:10:00	38	1	10	7	13	5	0	Salida de vía por posible distracción del conductor.
496	2025-12-02	08:10:00	48	2	8	8	3	9	0	Colisión por alcance en zona de visibilidad reducida.
497	2026-01-26	03:17:00	51	1	8	7	8	3	0	Colisión por alcance en zona de visibilidad reducida.
498	2025-12-10	02:10:00	25	2	9	8	12	9	0	Atestado pendiente de completar por la unidad de tráfico.
499	2025-12-31	03:48:00	13	3	7	9	8	9	0	Maniobra evasiva resultando en choque lateral.
500	2025-12-20	10:21:00	43	1	12	8	19	4	0	Incidente en tramo recto con asfalto seco.
502	2026-04-10	08:58:00	3	4	9	8	1	2	1	Accidente de vehículo 4x4
\.


--
-- TOC entry 3859 (class 0 OID 16391)
-- Dependencies: 216
-- Data for Name: carreteras; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carreteras (id, nombre, tipo) FROM stdin;
1	A-6	Autovía
2	A-50	Autovía
3	AP-6	Autopista
4	AP-51	Autopista
5	N-110	Nacional
6	N-403	Nacional
7	N-501	Nacional
8	N-502	Nacional
9	CL-501	Autonómica
10	CL-505	Autonómica
11	CL-507	Autonómica
12	CL-605	Autonómica
13	CL-610	Autonómica
14	AV-804	Autonómica
15	AV-905	Autonómica
16	AV-P-101	Provincial
17	AV-P-102	Provincial
18	AV-P-103	Provincial
19	AV-P-104	Provincial
20	AV-P-105	Provincial
21	AV-P-106	Provincial
22	AV-P-107	Provincial
23	AV-P-108	Provincial
24	AV-P-109	Provincial
25	AV-P-110	Provincial
26	AV-P-201	Provincial
27	AV-P-202	Provincial
28	AV-P-203	Provincial
29	AV-P-204	Provincial
30	AV-P-205	Provincial
31	AV-P-206	Provincial
32	AV-P-301	Provincial
33	AV-P-302	Provincial
34	AV-P-303	Provincial
35	AV-P-304	Provincial
36	AV-P-305	Provincial
37	AV-P-306	Provincial
38	AV-P-307	Provincial
39	AV-P-308	Provincial
40	AV-P-309	Provincial
41	AV-P-310	Provincial
42	AV-P-401	Provincial
43	AV-P-402	Provincial
44	AV-P-403	Provincial
45	AV-P-404	Provincial
46	AV-P-501	Provincial
47	AV-P-502	Provincial
48	AV-P-503	Provincial
49	AV-P-601	Provincial
50	AV-P-602	Provincial
51	AV-P-603	Provincial
\.


--
-- TOC entry 3861 (class 0 OID 16398)
-- Dependencies: 218
-- Data for Name: causas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.causas (id, descripcion) FROM stdin;
7	Exceso de velocidad
8	Distracción (Móvil)
9	Consumo alcohol/drogas
10	Cansancio/Sueño
11	Fallo mecánico
12	Animal en calzada
\.


--
-- TOC entry 3863 (class 0 OID 16405)
-- Dependencies: 220
-- Data for Name: clima; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clima (id, descripcion) FROM stdin;
6	Despejado
7	Lluvia
8	Nieve
9	Niebla
10	Viento fuerte
\.


--
-- TOC entry 3865 (class 0 OID 16412)
-- Dependencies: 222
-- Data for Name: gravedad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gravedad (id, nivel) FROM stdin;
1	Leve (sin heridos)
2	Leve (con heridos)
3	Grave
4	Mortal
\.


--
-- TOC entry 3878 (class 0 OID 0)
-- Dependencies: 223
-- Name: accidentes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accidentes_id_seq', 502, true);


--
-- TOC entry 3879 (class 0 OID 0)
-- Dependencies: 215
-- Name: carreteras_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carreteras_id_seq', 51, true);


--
-- TOC entry 3880 (class 0 OID 0)
-- Dependencies: 217
-- Name: causas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.causas_id_seq', 12, true);


--
-- TOC entry 3881 (class 0 OID 0)
-- Dependencies: 219
-- Name: clima_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clima_id_seq', 10, true);


--
-- TOC entry 3882 (class 0 OID 0)
-- Dependencies: 221
-- Name: gravedad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gravedad_id_seq', 4, true);


--
-- TOC entry 3710 (class 2606 OID 16427)
-- Name: accidentes accidentes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes
    ADD CONSTRAINT accidentes_pkey PRIMARY KEY (id);


--
-- TOC entry 3702 (class 2606 OID 16396)
-- Name: carreteras carreteras_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreteras
    ADD CONSTRAINT carreteras_pkey PRIMARY KEY (id);


--
-- TOC entry 3704 (class 2606 OID 16403)
-- Name: causas causas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.causas
    ADD CONSTRAINT causas_pkey PRIMARY KEY (id);


--
-- TOC entry 3706 (class 2606 OID 16410)
-- Name: clima clima_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clima
    ADD CONSTRAINT clima_pkey PRIMARY KEY (id);


--
-- TOC entry 3708 (class 2606 OID 16417)
-- Name: gravedad gravedad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gravedad
    ADD CONSTRAINT gravedad_pkey PRIMARY KEY (id);


--
-- TOC entry 3711 (class 2606 OID 16428)
-- Name: accidentes accidentes_carretera_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes
    ADD CONSTRAINT accidentes_carretera_id_fkey FOREIGN KEY (carretera_id) REFERENCES public.carreteras(id);


--
-- TOC entry 3712 (class 2606 OID 16438)
-- Name: accidentes accidentes_causa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes
    ADD CONSTRAINT accidentes_causa_id_fkey FOREIGN KEY (causa_id) REFERENCES public.causas(id);


--
-- TOC entry 3713 (class 2606 OID 16443)
-- Name: accidentes accidentes_clima_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes
    ADD CONSTRAINT accidentes_clima_id_fkey FOREIGN KEY (clima_id) REFERENCES public.clima(id);


--
-- TOC entry 3714 (class 2606 OID 16433)
-- Name: accidentes accidentes_gravedad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accidentes
    ADD CONSTRAINT accidentes_gravedad_id_fkey FOREIGN KEY (gravedad_id) REFERENCES public.gravedad(id);


-- Completed on 2026-05-05 13:47:33 CEST

--
-- PostgreSQL database dump complete
--

\unrestrict H7gKyXFOf6h4CNs2FXuqvYz83fuiz6IW8lpAAkWZrc80N2Z2ENbhJG3O20QXp4t

