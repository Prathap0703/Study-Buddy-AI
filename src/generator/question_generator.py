from groq import AuthenticationError, NotFoundError
from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion,FillBlankQuestion
from src.prompts.templates import mcq_prompt_template,fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.logging.logger import get_logger
from src.exception.exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)

    def _retry_and_parse(self,prompt,parser,topic,difficulty):

        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic {topic} with difficulty {difficulty}")

                response = self.llm.invoke(prompt.format(topic=topic , difficulty=difficulty))

                parsed = parser.parse(response.content)

                self.logger.info("Sucesfully parsed the question")

                return parsed

            except NotFoundError as e:
                # A retired or inaccessible model fails identically on every
                # attempt, so retrying just delays the error by three round
                # trips and buries the cause under a generic message.
                self.logger.error(f"Model '{settings.MODEL_NAME}' unavailable : {str(e)}")
                raise CustomException(
                    f"The model '{settings.MODEL_NAME}' is not available on your Groq "
                    f"account - it has most likely been retired. Pick a current model "
                    f"from https://console.groq.com/docs/models and set MODEL_NAME in "
                    f"your .env (or in the app secrets when deploying).",
                    show_details=False
                ) from e

            except AuthenticationError as e:
                # Same reasoning: a rejected key will not start working on retry.
                self.logger.error(f"Groq rejected the API key : {str(e)}")
                raise CustomException(
                    "Groq rejected the API key. Check GROQ_API_KEY in your .env "
                    "(or in the app secrets when deploying) - you can issue a new "
                    "key at https://console.groq.com/keys.",
                    show_details=False
                ) from e

            except Exception as e:
                self.logger.error(f"Error coming : {str(e)}")
                if attempt==settings.MAX_RETRIES-1:
                    raise CustomException(f"Generation failed after {settings.MAX_RETRIES} attempts", e)
                
    
    def generate_mcq(self,topic:str,difficulty:str='medium') -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question = self._retry_and_parse(mcq_prompt_template,parser,topic,difficulty)

            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ Structure")
            
            self.logger.info("Generated a valid MCQ Question")
            return question
        
        except CustomException:
            raise  # already carries an actionable message

        except Exception as e:
            self.logger.error(f"Failed to generate MCQ : {str(e)}")
            raise CustomException("MCQ generation failed" , e)
        
    
    def generate_fill_blank(self,topic:str,difficulty:str='medium') -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(fill_blank_prompt_template,parser,topic,difficulty)

            if "___" not in question.question:
                raise ValueError("Fill in blanks should contain '___'")
            
            self.logger.info("Generated a valid Fill in Blanks Question")
            return question
        
        except CustomException:
            raise  # already carries an actionable message

        except Exception as e:
            self.logger.error(f"Failed to generate fillups : {str(e)}")
            raise CustomException("Fill in blanks generation failed" , e)

