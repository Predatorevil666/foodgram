import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
        <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
            <div className={styles.text}>
              <ul className={styles.textItem}>
                <li className={styles.textItem}>
                  <a href="https://www.python.org/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080" alt="Python" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.djangoproject.com/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080" alt="Django" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.django-rest-framework.org/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080" alt="Django REST Framework" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.postgresql.org/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080" alt="PostgreSQL" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://nginx.org/ru/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080" alt="NGINX" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://gunicorn.org/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080" alt="gunicorn" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.docker.com/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080" alt="Docker" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.docker.com/" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080" alt="Docker compose" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://www.docker.com/products/docker-hub" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080" alt="Docker Hub" />
                  </a>
                </li>
                <li className={styles.textItem}>
                  <a href="https://github.com/features/actions" target="_blank" rel="noopener noreferrer">
                    <img src="https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080" alt="GitHub Actions" />
                  </a>
                </li>
              </ul>
            </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

