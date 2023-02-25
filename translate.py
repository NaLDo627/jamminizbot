from googletrans import Translator
import langid


translator = Translator()


async def translate_internal(ctx, author, text):
    translation = await translate_message(text)
    await ctx.send(f"<@{author.id}> says: \n{translation}")


async def translate_message(text):
    # Detect the language of the text
    source_lang, _ = langid.classify(text)
    if source_lang == 'ko':
        translation = translator.translate(text, src=source_lang, dest='ja').text
        translation += "\n\n" + translator.translate(text, src=source_lang, dest='en').text
    elif source_lang == 'ja':
        translation = translator.translate(text, src=source_lang, dest='ko').text
        translation += "\n\n" + translator.translate(text, src=source_lang, dest='en').text
    elif source_lang == 'en':
        translation = translator.translate(text, src=source_lang, dest='ko').text
        translation += "\n\n" + translator.translate(text, src=source_lang, dest='ja').text
    else:
        translation = translator.translate(text, src=source_lang, dest='en').text
    return translation
