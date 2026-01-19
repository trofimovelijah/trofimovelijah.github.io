#!/usr/bin/env python3
"""
Генератор HTML портфолио из Markdown файлов
Читает content/*.md и заполняет шаблон index.html.tpl
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

class MarkdownToHTML:
    """Преобразует Markdown в HTML"""
    
    @staticmethod
    def bold(text: str) -> str:
        """Преобразует **текст** в <strong>текст</strong>"""
        return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    @staticmethod
    def italic(text: str) -> str:
        """Преобразует *текст* в <em>текст</em>"""
        return re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    @staticmethod
    def paragraphs(text: str) -> str:
        """Преобразует параграфы в <p> теги"""
        lines = text.strip().split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Применяем форматирование
                line = MarkdownToHTML.bold(line)
                line = MarkdownToHTML.italic(line)
                result.append(f'<p>{line}</p>')
        
        return '\n'.join(result)
    
    @staticmethod
    def convert(text: str) -> str:
        """Конвертирует markdown в HTML"""
        text = MarkdownToHTML.bold(text)
        text = MarkdownToHTML.italic(text)
        return text

class PortfolioGenerator:
    def __init__(self, content_dir='content', template_file='templates/index.html.tpl', output_file='index.html'):
        self.content_dir = Path(content_dir)
        self.template_file = Path(template_file)
        self.output_file = Path(output_file)
        self.data = {}
        
    def read_file(self, filepath: Path) -> str:
        """Безопасно читает файл"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f'⚠️  Файл не найден: {filepath}')
            return ''
        except Exception as e:
            print(f'❌ Ошибка при чтении {filepath}: {e}')
            return ''
    
    def write_file(self, filepath: Path, content: str) -> bool:
        """Безопасно пишет файл"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f'❌ Ошибка при записи {filepath}: {e}')
            return False
    
    def parse_about(self) -> Dict[str, Any]:
        """Парсит about.md"""
        print('📖 Парсю about.md...')
        about_file = self.content_dir / 'about.md'
        content = self.read_file(about_file)
        
        if not content:
            return {'intro': '', 'focus': '', 'skills': []}
        
        result = {'intro': '', 'focus': '', 'skills': []}
        
        # Извлекаем основной текст (до первого ##)
        intro_match = re.search(r'^#\s+.+?\n\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if intro_match:
            intro_text = intro_match.group(1).strip()
            # Берем первый параграф
            first_para = re.search(r'^(.+?)(?:\n\n|$)', intro_text, re.DOTALL)
            if first_para:
                intro_html = first_para.group(1).strip()
                intro_html = MarkdownToHTML.convert(intro_html)
                result['intro'] = intro_html
                print(f'   ✓ Введение найдено')
        
        # Извлекаем "Мой фокус" или "Фокус деятельности" (ГИБКО)
        # Поддерживаем разные варианты названия секции
        focus_patterns = [
            r'##\s+Мой\s+фокус\n(.*?)(?=##|\Z)',  # "Мой фокус"
            r'##\s+Фокус\s+деятельности\n(.*?)(?=##|\Z)',  # "Фокус деятельности"
            r'##\s+Фокус\n(.*?)(?=##|\Z)',  # "Фокус"
            r'##\s+(?:My\s+)?focus\n(.*?)(?=##|\Z)',  # English variants
        ]
        
        focus_text = None
        for pattern in focus_patterns:
            focus_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if focus_match:
                focus_text = focus_match.group(1).strip()
                print(f'   ✓ Раздел фокуса найден')
                break
        
        if focus_text:
            focus_html = MarkdownToHTML.paragraphs(focus_text)
            result['focus'] = focus_html
        else:
            print(f'   ⚠️  Раздел фокуса НЕ найден (проверь имя секции в about.md)')
        
        # Извлекаем навыки
        skills_match = re.search(r'##\s+Навыки\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            skills = re.findall(r'[-*]\s+(.+?)(?:\n|$)', skills_text)
            result['skills'] = skills
            print(f'   ✓ Найдено навыков: {len(skills)}')
        else:
            print(f'   ⚠️  Навыки НЕ найдены')
        
        return result

    
    def parse_projects(self) -> List[Dict[str, Any]]:
        """Парсит projects.md"""
        print('📦 Парсю projects.md...')
        projects_file = self.content_dir / 'projects.md'
        content = self.read_file(projects_file)
        
        if not content:
            return []
        
        projects = []
        
        # Разделяем по ### заголовкам
        project_blocks = re.findall(r'###\s+(.+?)\n(.*?)(?=###|\Z)', content, re.DOTALL)
        
        for project_name, project_content in project_blocks:
            project = {
                'name': project_name.strip(),
                'description': '',
                'tags': [],
                'link': '',
                'date': '',
                'icon': '📦'
            }
            
            # Описание (первый параграф)
            desc_match = re.search(r'^(.*?)(?:\n\n|\*\*|\Z)', project_content, re.DOTALL)
            if desc_match:
                desc = desc_match.group(1).strip()
                # Чистим маркдаун
                desc = MarkdownToHTML.convert(desc)
                project['description'] = desc
            
            # Теги
            tags_match = re.search(r'\*\*Теги:\*\*\s*(.+?)(?:\n|$)', project_content)
            if tags_match:
                tags_str = tags_match.group(1).strip()
                project['tags'] = [t.strip() for t in tags_str.split(',')]
            
            # Ссылка
            link_match = re.search(r'\*\*Ссылка:\*\*\s*(https?://[^\s]+)', project_content)
            if link_match:
                project['link'] = link_match.group(1).strip()
            
            # Дата
            date_match = re.search(r'\*\*Дата:\*\*\s*(.+?)(?:\n|$)', project_content)
            if date_match:
                project['date'] = date_match.group(1).strip()
            
            # Иконка (опционально)
            icon_match = re.search(r'\*\*Иконка:\*\*\s*(.+?)(?:\n|$)', project_content)
            if icon_match:
                project['icon'] = icon_match.group(1).strip()
            
            if project['link']:  # Добавляем только если есть ссылка
                projects.append(project)
                print(f'   ✓ Добавлен проект: {project["name"]}')
        
        print(f'   ✅ Найдено проектов: {len(projects)}')
        return projects
    
    def parse_resources(self) -> List[Dict[str, Any]]:
        """Парсит resources.md"""
        print('🔗 Парсю resources.md...')
        resources_file = self.content_dir / 'resources.md'
        content = self.read_file(resources_file)
        
        if not content:
            return []
        
        resources = []
        icon_map = {
            'GitHub': '🐙',
            'GitFlic': '🇷🇺',
            'Hugging Face': '🤗',
            'Google Docs': '📚',
            'Medium': '✍️',
            'LinkedIn': '💼',
            'Twitter': '𝕏',
        }
        
        # Разделяем по ### заголовкам
        resource_blocks = re.findall(r'###\s+(.+?)\n(.*?)(?=###|\Z)', content, re.DOTALL)
        
        for resource_name, resource_content in resource_blocks:
            resource = {
                'name': resource_name.strip(),
                'description': '',
                'link': '',
                'icon': icon_map.get(resource_name.strip(), '🔗')
            }
            
            # Описание (первый параграф)
            desc_match = re.search(r'^(.*?)(?:\n\n|https?://|\Z)', resource_content, re.DOTALL)
            if desc_match:
                resource['description'] = desc_match.group(1).strip()
            
            # Ссылка
            link_match = re.search(r'https?://[^\s\n]+', resource_content)
            if link_match:
                resource['link'] = link_match.group(0)
            
            if resource['link']:
                resources.append(resource)
                print(f'   ✓ Добавлен ресурс: {resource["name"]}')
        
        print(f'   ✅ Найдено ресурсов: {len(resources)}')
        return resources
    
    def parse_contact(self) -> Dict[str, Any]:
        """Парсит contact.md"""
        print('📞 Парсю contact.md...')
        contact_file = self.content_dir / 'contact.md'
        content = self.read_file(contact_file)
        
        if not content:
            return {'message': '', 'social': []}
        
        result = {'message': '', 'social': []}
        
        # Основное сообщение
        msg_match = re.search(r'^#\s+.+?\n\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if msg_match:
            result['message'] = msg_match.group(1).strip()
        
        # Соцсети
        social_match = re.search(r'##\s+Социальные сети\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if social_match:
            social_text = social_match.group(1).strip()
            socials = re.findall(r'[-*]\s+\[(.+?)\]\((.+?)\)', social_text)
            result['social'] = [{'name': name, 'link': link} for name, link in socials]
            print(f'   ✓ Найдено соцсетей: {len(result["social"])}')
        
        print(f'   ✅ Найдено контактов: {len(result["social"])}')
        return result
    
    def generate_projects_html(self, projects: List[Dict[str, Any]]) -> str:
        """Генерирует HTML для проектов"""
        if not projects:
            return '<p>Проекты еще не добавлены</p>'
        
        projects_html = ''
        
        for project in projects:
            tags_html = ''.join([
                f'<span class="tag">{tag}</span>'
                for tag in project.get('tags', [])
            ])
            
            projects_html += f'''
                <div class="project-card">
                    <div class="project-icon">{project.get('icon', '📦')}</div>
                    <h3>{project['name']}</h3>
                    <p>{project.get('description', '')}</p>
                    <div class="project-tags">
                        {tags_html}
                    </div>
                    <a href="{project['link']}" class="project-link" target="_blank">
                        На ресурсе →
                    </a>
                </div>
            '''
        
        return projects_html
    
    def generate_resources_html(self, resources: List[Dict[str, Any]]) -> str:
        """Генерирует HTML для ресурсов"""
        if not resources:
            return '<p>Ресурсы еще не добавлены</p>'
        
        resources_html = ''
        
        for resource in resources:
            resources_html += f'''
                <div class="resource-card">
                    <div class="resource-icon">{resource.get('icon', '🔗')}</div>
                    <h3>{resource['name']}</h3>
                    <p>{resource.get('description', '')}</p>
                    <a href="{resource['link']}" target="_blank">Перейти</a>
                </div>
            '''
        
        return resources_html
    
    def generate_social_html(self, social: List[Dict[str, str]]) -> str:
        """Генерирует HTML для соцсетей"""
        social_map = {
            'GitHub': 'GH',
            'LinkedIn': 'IN',
            'Twitter': 'X',
            'Email': '✉️'
        }
        
        social_html = ''
        for item in social:
            label = social_map.get(item['name'], item['name'][:2].upper())
            target = '_blank' if 'mailto' not in item['link'] else ''
            social_html += f'<a href="{item["link"]}" class="social-link" target="{target}">{label}</a>\n                '
        
        return social_html
    
    def generate(self) -> bool:
        """Главный метод генерации"""
        print('\n🚀 Начинаю генерацию HTML...\n')
        
        # Проверяем наличие файлов
        if not self.template_file.exists():
            print(f'❌ Шаблон не найден: {self.template_file}')
            return False
        
        if not self.content_dir.exists():
            print(f'❌ Директория контента не найдена: {self.content_dir}')
            return False
        
        # Парсим все файлы
        about_data = self.parse_about()
        projects = self.parse_projects()
        resources = self.parse_resources()
        contact = self.parse_contact()
        
        # Генерируем HTML части
        projects_html = self.generate_projects_html(projects)
        resources_html = self.generate_resources_html(resources)
        
        skills_html = '\n                '.join([
            f'<div class="skill-tag">{skill}</div>'
            for skill in about_data.get('skills', [])
        ])
        
        social_html = self.generate_social_html(contact['social'])
        
        # Читаем шаблон
        template = self.read_file(self.template_file)
        
        if not template:
            print('❌ Не удалось прочитать шаблон')
            return False
        
        # Заменяем плейсхолдеры
        html = template
        html = html.replace('{{ABOUT_INTRO}}', about_data.get('intro', '<p>Информация не заполнена</p>'))
        html = html.replace('{{ABOUT_FOCUS}}', about_data.get('focus', '<p>Информация не заполнена</p>'))
        html = html.replace('{{SKILLS_TAGS}}', skills_html)
        html = html.replace('{{PROJECTS}}', projects_html)
        html = html.replace('{{RESOURCES}}', resources_html)
        html = html.replace('{{SOCIAL_LINKS}}', social_html)
        html = html.replace('{{CONTACT_MESSAGE}}', contact.get('message', ''))
        html = html.replace('{{PROJECTS_COUNT}}', str(len(projects)) + ('+' if len(projects) >= 5 else ''))
        html = html.replace('{{SKILLS_COUNT}}', str(len(about_data.get('skills', []))))
        
        # Пишем результат
        if self.write_file(self.output_file, html):
            print(f'\n✅ HTML успешно сгенерирован: {self.output_file}')
            print(f'\n📊 Статистика:')
            print(f'   📦 Проектов: {len(projects)}')
            print(f'   🔗 Ресурсов: {len(resources)}')
            print(f'   🎯 Навыков: {len(about_data.get("skills", []))}')
            print(f'   👥 Контактов: {len(contact["social"])}')
            print(f'\n✨ Генерация завершена!\n')
            return True
        
        return False

def main():
    try:
        generator = PortfolioGenerator()
        success = generator.generate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'\n❌ Критическая ошибка: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

