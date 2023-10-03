class onlineCourse:
    def __init__(self, courseId, name, videos, price, image, studentPurchaseList, refundDescription, courseContent, requirements, description, courseForWho, instructor):
        self.courseId = courseId
        self.videos = videos
        self.price = price
        self.name = name
        self.image = image
        self.studentPurchaseList = studentPurchaseList if studentPurchaseList else []
        self.refundDescription = refundDescription
        self.courseContent = courseContent
        self.requirements = requirements
        self.description = description
        self.courseForWho = courseForWho
        self.instructor = instructor

    def to_dict(self):
        return {
            'courseId': self.courseId,
            'videos': self.videos,
            'price': self.price,
            'name': self.name,
            'image': self.image,
            'studentPurchaseList': self.studentPurchaseList,
            'refundDescription': self.refundDescription,
            'courseContent': self.courseContent,
            'requirements': self.requirements,
            'description': self.description,
            'courseForWho': self.courseForWho,
            'instructor': self.instructor
        }
    
    def get_courseId(self):
        return self.courseId