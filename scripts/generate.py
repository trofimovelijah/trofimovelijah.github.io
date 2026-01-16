#!/usr/bin/env python3
"""
Генератор HTML из Markdown контента
Читает content/portfolio.md и заполняет шаблон
"""

import re
import os
from pathlib import Path

def read_file(path):
    """Читает файл"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """Пишет файл"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_markdown(md_content):
    """Парсит markdown и извлекает структурированные данные"""
    
    # Извлекаем секции по заголовкам
    data = {
        'about': '',
        'projects': [],
        'resources': [],
        'skills': [],
        'social': {}
    }
    
    # Парс "Обо мне"
    about_match = re.search(r'## Обо мне(.*?)(?=## |\Z)', md_content, re.DOTALL)
    if about_match:
        about_text = about_match.group(1).strip()
        # Извлекаем текст и подзаголовки
        lines = about_text.split('\n')
        intro = []
        sections = {}
        current_section = None
        
        for line in lines:
            if line.startswith('###'):
                current_section = line.replace('###', '').strip()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line.strip())
            elif not current_section and line.strip() and not line.startswith('#'):
                intro.append(line.strip())
        
        # Собираем HTML для об авторе
        about_html = '<h3>Кто я</h3>'
        for line in intro:
            if line.strip():
                about_html += f'<p>{line.strip()}</p>'
        
        about_html += '<h3>Мой фокус</h3>'
        for section, content in sections.items():
            if section and content:
                about_html += f'<p><strong>{section}:</strong> {" ".join(content)}</p>'
        
        data['about'] = about_html
    
    # Парс Навыков
    skills_match = re.search(r'### Навыки(.*?)(?=## |\Z)', md_content, re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        skills = re.findall(r'- (.+)', skills_text)
        for skill in skills:
            data['skills'].append(f'<div class="skill-tag">{skill}</div>')
    
    # Парс Проектов
    projects_match = re.search(r'## Проекты(.*?)(?=## |\Z)', md_content, re.DOTALL)
    if projects_match:
        projects_text = projects_match.group(1)
        # Разделяем по подзаголовкам ###
        project_blocks = re.findall(r'### (.+?)\n(.*?)(?=###|\Z)', projects_text, re.DOTALL)
        
        for project_name, project_content in project_blocks:
            project_data = {'name': project_name.strip()}
            
            # Извлекаем описание
            desc = re.search(r'^(.*?)(?=\*\*|\Z)', project_content, re.DOTALL)
            if desc:
                project_data['desc'] = desc.group(1).strip()
            
            # Извлекаем теги
            tags = re.findall(r'\*\*Теги:\*\*\s*(.+)', project_content)
            if tags:
                project_data['tags'] = [t.strip() for t in tags[0].split(',')]
            
            # Извлекаем ссылку
            link = re.search(r'\*\*Ссылка:\*\*\s*(.+)', project_content)
            if link:
                project_data['link'] = link.group(1).strip()
            
            # Извлекаем дату
            date = re.search(r'\*\*Дата:\*\*\s*(.+)', project_content)
            if date:
                project_data['date'] = date.group(1).strip()
            
            if 'link' in project_data:
                data['projects'].append(project_data)
    
    # Парс Ресурсов
    resources_match = re.search(r'## Ресурсы(.*?)(?=## |\Z)', md_content, re.DOTALL)
    if resources_match:
        resources_text = resources_match.group(1)
        resource_blocks = re.findall(r'### (.+?)\n(.*?)(?=###|\Z)', resources_text, re.DOTALL)
        
        for resource_name, resource_content in resource_blocks:
            resource_data = {'name': resource_name.strip()}
            
            # Описание
            desc = re.search(r'^(.*?)\n\nhttps', resource_content, re.DOTALL)
            if desc:
                resource_data['desc'] = desc.group(1).strip()
            
            # Ссылка
            link = re.search(r'https?[^\s\n]+', resource_content)
            if link:
                resource_data['link'] = link.group(0)
            
            if 'link' in resource_data:
                data['resources'].append(resource_data)
    
    return data

def generate_html(template_path, data):
    """Генерирует HTML из шаблона и данных"""
    template = read_file(template_path)
    
    # Генерируем HTML для about
    template = template.replace('{{ABOUT_SECTION}}', data['about'])
    
    # Генерируем skills tags
    skills_html = '\n                '.join(data['skills'])
    template = template.replace('{{SKILLS_TAGS}}', skills_html)
    
    # Генерируем проекты
    projects_html = ''
    for project in data['projects']:
        tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in project.get('tags', [])])
        project_icon = '📦'  # Можно сделать более умным
        
        projects_html += f'''
                <div class="project-card">
                    <div class="project-icon">{project_icon}</div>
                    <h3>{project['name']}</h3>
                    <p>{project.get('desc', '')}</p>
                    <div class="project-tags">
                        {tags_html}
                    </div>
                    <a href="{project['link']}" class="project-link" target="_blank">
                        На ресурсе →
                    </a>
                </div>
        '''
    template = template.replace('{{PROJECTS}}', projects_html)
    
    # Генерируем ресурсы
    resources_html = ''
    resource_icons = {
        'GitHub': '🐙',
        'GitFlic': '🇷🇺',
        'Hugging Face': '🤗',
        'Google Docs': '📚',
        'Контакты': '💬',
        'Блог': '✍️'
    }
    
    for resource in data['resources']:
        icon = resource_icons.get(resource['name'], '🔗')
        resources_html += f'''
                <div class="resource-card">
                    <div class="resource-icon">{icon}</div>
                    <h3>{resource['name']}</h3>
                    <p>{resource.get('desc', '')}</p>
                    <a href="{resource['link']}" target="_blank">Перейти</a>
                </div>
        '''
    template = template.replace('{{RESOURCES}}', resources_html)
    
    # Генерируем соцсети (из ресурсов извлекаем контакты)
    social_html = ''
    social_icons = {
        'https://github.com': 'GH',
        'https://linkedin.com': 'IN',
        'https://twitter.com': 'X',
        'mailto:': '✉️'
    }
    
    for resource in data['resources']:
        link = resource.get('link', '')
        for url_pattern, label in social_icons.items():
            if url_pattern in link:
                social_html += f'<a href="{link}" class="social-link" target="_blank">{label}</a>\n                '
                break
    
    template = template.replace('{{SOCIAL_LINKS}}', social_html)
    
    # Количество проектов
    template = template.replace('{{PROJECTS_COUNT}}', str(len(data['projects'])) + '+')
    
    return template

def main():
    """Главная функция"""
    # Пути
    content_path = 'content/portfolio.md'
    template_path = 'templates/index.html.template'
    output_path = 'index.html'
    
    # Проверяем наличие файлов
    if not os.path.exists(content_path):
        print(f'❌ Файл {content_path} не найден!')
        return False
    
    if not os.path.exists(template_path):
        print(f'❌ Файл {template_path} не найден!')
        return False
    
    # Читаем markdown
    md_content = read_file(content_path)
    
    # Парсим
    data = parse_markdown(md_content)
    
    # Генерируем HTML
    html_content = generate_html(template_path, data)
    
    # Пишем результат
    write_file(output_path, html_content)
    
    print(f'✅ HTML успешно сгенерирован: {output_path}')
    print(f'   📦 Проектов: {len(data["projects"])}')
    print(f'   🔗 Ресурсов: {len(data["resources"])}')
    print(f'   🎯 Навыков: {len(data["skills"])}')
    
    return True

if __name__ == '__main__':
    main()

