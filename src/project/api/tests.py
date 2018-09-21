from django.test import TestCase
from django.shortcuts import reverse
from rest_framework import status
from django.contrib.auth.models import User

from account.models import StudentProfile, MentorProfile
from project.models import Project


class ProjectViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.student = User.objects.create_user(username='student', email='student@test.com', password='password')
        cls.mentor = User.objects.create_user(username='mentor', email='mentor@test.com', password='password')
        cls.student_profile = StudentProfile.objects.create(user=cls.student, phone='9999999999',
                                                            github='https://github.com',
                                                            year=StudentProfile.YEAR_CHOICES[0][0],
                                                            gender=StudentProfile.GENDER_CHOICES[0][0],
                                                            branch=StudentProfile.BRANCH_CHOICES[0][0])
        cls.mentor_profile = MentorProfile.objects.create(user=cls.mentor, phone='9999999999',
                                                          github='https://github.com',
                                                          year=StudentProfile.YEAR_CHOICES[0][0],
                                                          gender=StudentProfile.GENDER_CHOICES[0][0],
                                                          branch=StudentProfile.BRANCH_CHOICES[0][0])

    def test_status_OK(self):
        project = Project.objects.create(name='Project 1', github_link='https://github.com', description='Description')
        project.mentors.add(self.mentor_profile)
        project.save()
        response = self.client.get(reverse('api:project:projects-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode('utf-8'),
                         '[{"id":1,"name":"Project 1","description":"Description","github_link":'
                         '"https://github.com","students":[],"mentors":[1]}]')

    def test_create(self):
        data = {
            'name': 'Project 2',
            'github_link': 'https://github.com',
            'description': 'Description',
            'mentors': [self.mentor_profile.id]
        }
        response = self.client.post(reverse('api:project:projects-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.login(username=self.mentor.username, password='password')
        response = self.client.post(reverse('api:project:projects-list'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(name='Project 2', mentors='{}'.format(self.mentor_profile.id)).exists())