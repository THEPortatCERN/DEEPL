from rest_framework import serializers

from classifier.models import ClassifiedDocument, ClassifiedExcerpt


class ClassifiedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for classified document"""
    classification = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedDocument
        fields = (
            'group_id', 'id', 'classification',
            'text', 'classification_confidence'
        )
        read_only_fields = ('id', )
        extra_kwargs = {
            'text': {'write_only': True},
        }

    def get_classification(self, obj):
        return obj.classification_probabilities

    def create(self, validated_data):
        # TODO: add classifier
        classification = validated_data['classification']
        return ClassifiedDocument.objects.create(
            text=validated_data['text'],
            classification_probabilities=classification,
            group_id=validated_data.get('group_id'),
            classification_label=classification[0][0],
            confidence=classification[0][1]
        )


class ClassifiedExcerptSerializer(serializers.ModelSerializer):
    """Serialiser for classified excerpt"""
    classification = serializers.SerializerMethodField()
    start_pos = serializers.SerializerMethodField()
    end_pos = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedExcerpt
        fields = (
            'start_pos', 'end_pos', 'classification',
            'classification_confidence'
        )

    def get_start_pos(self, obj):
        txt = obj.classified_document.text
        pos = obj.start_pos
        while txt[pos] in ' \n"?\'”' and pos < obj.end_pos:
            pos += 1
        return pos

    def get_end_pos(self, obj):
        txt = obj.classified_document.text
        pos = obj.end_pos
        while txt[pos] in ' \n"?\'”' and pos > obj.start_pos:
            pos-=1
        return pos

    def get_classification(self, obj):
        return obj.classification_probabilities

    # TODO: COMPLETE THIS
    def _create(self, validated_data):
        classification = validated_data['classification']
        return ClassifiedExcerpt.objects.create(
            start_pos=validated_data['start_pos'],
            end_pos=validated_data['end_pos'],
        )
